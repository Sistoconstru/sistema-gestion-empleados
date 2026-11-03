"""Tests de versiones y anexos de documentos.

Antes solo cabía un documento por tipo y reemplazar borraba el archivo
anterior de S3; tampoco había dónde poner un otrosí. Ahora RRHH actualiza un
documento aprobado guardando la versión anterior, y adjunta anexos al
contrato. El empleado ve la versión vigente y los anexos, no el historial.
"""
import shutil
import tempfile
from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.documents.models import AnexoDocumento, DocumentoEmpleado, TipoDocumentoEmpleado, VersionDocumento
from apps.employees.models import Empleado, EstadoEmpleado, TipoDocumento
from apps.organizational.models import Sede

User = get_user_model()

PDF = b'%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF'
MEDIA_TMP = tempfile.mkdtemp()


def pdf(nombre='contrato.pdf', contenido=PDF):
    return SimpleUploadedFile(nombre, contenido, content_type='application/pdf')


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class VersionesYAnexosTests(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TMP, ignore_errors=True)

    def crear_empleado(self, username, documento, staff=False):
        user = User.objects.create_user(username=username, password='x-9slek31', is_staff=staff)
        emp = Empleado.objects.create(
            usuario=user, tipo_documento=self.tipo_doc,
            nombres=username.split('.')[0].capitalize(), apellidos='Prueba',
            numero_documento=documento, telefono_contacto='3101234567',
            fecha_ingreso=date.today(), sede=self.sede, estado=self.estado,
            contacto_emergencia_telefono='3109876543', direccion='Calle 1',
            creado_por=user,
        )
        return user, emp

    def setUp(self):
        self.estado = EstadoEmpleado.objects.create(codigo='999', nombre='Activo')
        self.tipo_doc = TipoDocumento.objects.create(codigo='CC', nombre='Cédula')
        self.sede = Sede.objects.create(codigo='S1', nombre='Sede')
        self.rrhh, _ = self.crear_empleado('rrhh.prueba', '100', staff=True)
        self.user, self.empleado = self.crear_empleado('ana.prueba', '111')
        self.otro, _ = self.crear_empleado('beto.prueba', '222')

        self.tipo_contrato = TipoDocumentoEmpleado.objects.create(
            codigo='DCLAB', nombre='Contrato laboral', obligatorio=True,
            formatos_permitidos='PDF', admite_anexos=True,
        )
        self.tipo_cedula = TipoDocumentoEmpleado.objects.create(
            codigo='CED', nombre='Documento de identidad', formatos_permitidos='PDF',
        )
        self.contrato = DocumentoEmpleado.objects.create(
            empleado=self.empleado, tipo_documento=self.tipo_contrato,
            nombre_archivo='DCLAB_111.pdf', archivo=pdf(),
            estado_aprobacion='aprobado', aprobado_por=self.rrhh,
            fecha_aprobacion=timezone.now(), cargado_por=self.rrhh,
        )
        self.archivo_original = self.contrato.archivo.name

    def url(self, nombre, pk):
        return reverse(f'documents:{nombre}', args=[pk])

    # --- A. Versiones --------------------------------------------------------

    def actualizar(self, usuario, **extra):
        self.client.force_login(usuario)
        datos = {'archivo': pdf('nuevo.pdf'), 'motivo': 'Contrato a término indefinido', **extra}
        return self.client.post(self.url('documento_actualizar', self.contrato.pk), datos)

    def test_rrhh_actualiza_un_contrato_aprobado_y_guarda_la_version_anterior(self):
        self.actualizar(self.rrhh)
        self.contrato.refresh_from_db()
        self.assertEqual(self.contrato.version, 2)
        self.assertEqual(self.contrato.estado_aprobacion, 'aprobado')
        self.assertEqual(self.contrato.aprobado_por, self.rrhh)
        self.assertNotEqual(self.contrato.archivo.name, self.archivo_original)

        anterior = VersionDocumento.objects.get(documento=self.contrato)
        self.assertEqual(anterior.version, 1)
        self.assertEqual(anterior.archivo.name, self.archivo_original)
        self.assertEqual(anterior.motivo, 'Contrato a término indefinido')
        # El archivo original sigue existiendo.
        self.assertTrue(anterior.archivo.storage.exists(self.archivo_original))

    def test_el_empleado_no_puede_actualizar(self):
        r = self.actualizar(self.user)
        self.assertEqual(r.status_code, 403)
        self.assertFalse(VersionDocumento.objects.exists())

    def test_reemplazar_un_rechazado_ya_no_borra_el_archivo(self):
        self.contrato.estado_aprobacion = 'rechazado'
        self.contrato.motivo_rechazo = 'Ilegible'
        self.contrato.save()
        self.client.force_login(self.user)
        self.client.post(self.url('documento_replace', self.contrato.pk), {'archivo': pdf('otra.pdf')})
        anterior = VersionDocumento.objects.get(documento=self.contrato)
        self.assertEqual(anterior.archivo.name, self.archivo_original)
        self.assertTrue(anterior.archivo.storage.exists(self.archivo_original))

    def test_solo_rrhh_ve_y_descarga_versiones_anteriores(self):
        self.actualizar(self.rrhh)
        version = VersionDocumento.objects.get()

        self.client.force_login(self.user)
        r = self.client.get(self.url('documento_view', self.contrato.pk))
        self.assertNotContains(r, 'Versiones anteriores')
        self.assertEqual(self.client.get(self.url('version_descargar', version.pk)).status_code, 403)

        self.client.force_login(self.rrhh)
        r = self.client.get(self.url('documento_view', self.contrato.pk))
        self.assertContains(r, 'Versiones anteriores (1)')
        self.assertEqual(self.client.get(self.url('version_descargar', version.pk)).status_code, 200)

    # --- B. Anexos -----------------------------------------------------------

    def crear_anexo(self, usuario, documento=None):
        self.client.force_login(usuario)
        return self.client.post(self.url('anexo_crear', (documento or self.contrato).pk), {
            'tipo': 'otrosi', 'fecha_vigencia': '2026-11-01',
            'descripcion': 'Aumento salarial', 'archivo': pdf('otrosi.pdf'),
        })

    def test_rrhh_agrega_un_otrosi_al_contrato(self):
        self.crear_anexo(self.rrhh)
        anexo = AnexoDocumento.objects.get()
        self.assertEqual(anexo.documento, self.contrato)
        self.assertEqual(anexo.cargado_por, self.rrhh)
        self.assertEqual(anexo.nombre_archivo, 'OTROSI_111_20261101.pdf')
        # El contrato no cambia.
        self.contrato.refresh_from_db()
        self.assertEqual(self.contrato.version, 1)
        self.assertEqual(self.contrato.estado_aprobacion, 'aprobado')

    def test_el_empleado_no_puede_agregar_anexos(self):
        r = self.crear_anexo(self.user)
        self.assertEqual(r.status_code, 403)
        self.assertFalse(AnexoDocumento.objects.exists())

    def test_un_tipo_sin_anexos_no_los_acepta(self):
        cedula = DocumentoEmpleado.objects.create(
            empleado=self.empleado, tipo_documento=self.tipo_cedula,
            nombre_archivo='CED_111.pdf', archivo=pdf('ced.pdf'), cargado_por=self.rrhh,
        )
        self.crear_anexo(self.rrhh, documento=cedula)
        self.assertFalse(AnexoDocumento.objects.exists())

    def test_el_empleado_ve_y_descarga_sus_anexos(self):
        self.crear_anexo(self.rrhh)
        anexo = AnexoDocumento.objects.get()
        self.client.force_login(self.user)
        r = self.client.get(self.url('documento_view', self.contrato.pk))
        self.assertContains(r, 'Otrosí')
        self.assertContains(r, 'Aumento salarial')
        self.assertEqual(self.client.get(self.url('anexo_descargar', anexo.pk)).status_code, 200)

    def test_otro_empleado_no_descarga_anexos_ajenos(self):
        self.crear_anexo(self.rrhh)
        anexo = AnexoDocumento.objects.get()
        self.client.force_login(self.otro)
        self.assertEqual(self.client.get(self.url('anexo_descargar', anexo.pk)).status_code, 403)

    def test_rrhh_elimina_un_anexo_cargado_por_error(self):
        self.crear_anexo(self.rrhh)
        anexo = AnexoDocumento.objects.get()
        ruta = anexo.archivo.name
        self.client.post(self.url('anexo_eliminar', anexo.pk))
        self.assertFalse(AnexoDocumento.objects.exists())
        self.assertFalse(anexo.archivo.storage.exists(ruta))

    def test_la_lista_muestra_cuantos_anexos_tiene_el_contrato(self):
        self.crear_anexo(self.rrhh)
        r = self.client.get(reverse('documents:empleado_documentos', args=[self.empleado.pk]))
        self.assertContains(r, '1 anexo')
