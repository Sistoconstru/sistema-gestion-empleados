/**
 * =============================================================================
 * Custom JavaScript for RRHH Pro Sistema de Gestión de Empleados
 * =============================================================================
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initializeTooltips();
    initializePopovers();
    initializeFormValidation();
    initializeConfirmations();
    initializeSearch();
    initializeExportButtons();
    initializeAnimations();
    
    console.log('🚀 RRHH Pro JS initialized');
});

/**
 * Inicializar tooltips de Bootstrap
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            delay: { show: 500, hide: 100 }
        });
    });
}

/**
 * Inicializar popovers de Bootstrap
 */
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Validaciones de formulario en tiempo real
 */
function initializeFormValidation() {
    // Validación de números de documento
    const docInputs = document.querySelectorAll('#id_numero_documento, input[name*="documento"]');
    docInputs.forEach(input => {
        input.addEventListener('input', function() {
            // Solo permitir números
            this.value = this.value.replace(/\D/g, '');
            
            // Validar longitud mínima
            if (this.value.length < 6 && this.value.length > 0) {
                this.setCustomValidity('El número de documento debe tener al menos 6 dígitos');
            } else {
                this.setCustomValidity('');
            }
        });
    });
    
    // Formateo de teléfonos
    const phoneInputs = document.querySelectorAll('#id_telefono_contacto, #id_contacto_emergencia_telefono, input[name*="telefono"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    });
    
    // Validación de emails
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateEmail(this);
        });
    });
    
    // Confirmación de contraseña (si existe)
    const passwordConfirm = document.querySelector('#id_confirmar_email');
    const passwordOriginal = document.querySelector('#id_correo_electronico');
    
    if (passwordConfirm && passwordOriginal) {
        passwordConfirm.addEventListener('input', function() {
            if (this.value !== passwordOriginal.value) {
                this.setCustomValidity('Los correos electrónicos no coinciden');
            } else {
                this.setCustomValidity('');
            }
        });
    }
}

/**
 * Formatear número de teléfono colombiano
 */
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    
    // Formatear según longitud
    if (value.length === 10) {
        // Formato: 300 123 4567
        value = value.replace(/(\d{3})(\d{3})(\d{4})/, '$1 $2 $3');
    } else if (value.length === 7) {
        // Formato: 123 4567
        value = value.replace(/(\d{3})(\d{4})/, '$1 $2');
    } else if (value.startsWith('57') && value.length === 12) {
        // Formato internacional: +57 300 123 4567
        value = '+' + value.replace(/(\d{2})(\d{3})(\d{3})(\d{4})/, '$1 $2 $3 $4');
    }
    
    input.value = value;
}

/**
 * Validar formato de email
 */
function validateEmail(input) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (input.value && !emailRegex.test(input.value)) {
        input.setCustomValidity('Ingrese un email válido');
        input.classList.add('is-invalid');
    } else {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
    }
}

/**
 * Confirmaciones para acciones importantes
 */
function initializeConfirmations() {
    // Botones de eliminación
    const deleteButtons = document.querySelectorAll('.btn-delete, .delete-action');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const itemName = this.dataset.itemName || 'este elemento';
            
            if (confirm(`¿Estás seguro de que deseas eliminar ${itemName}?`)) {
                // Proceder con la acción
                if (this.href) {
                    window.location.href = this.href;
                } else if (this.form) {
                    this.form.submit();
                }
            }
        });
    });
    
    // Botones de cambio de estado
    const statusButtons = document.querySelectorAll('.btn-status-change');
    statusButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const newStatus = this.dataset.newStatus;
            const itemName = this.dataset.itemName || 'este elemento';
            
            if (!confirm(`¿Cambiar el estado de ${itemName} a ${newStatus}?`)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Búsqueda en tiempo real
 */
function initializeSearch() {
    const searchInputs = document.querySelectorAll('.search-input, input[name="search"]');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            // Debounce de 300ms
            searchTimeout = setTimeout(() => {
                const query = this.value.trim();
                
                if (query.length >= 2) {
                    performSearch(query);
                } else if (query.length === 0) {
                    clearSearchResults();
                }
            }, 300);
        });
    });
}

/**
 * Realizar búsqueda AJAX (ejemplo)
 */
function performSearch(query) {
    // Aquí implementar búsqueda AJAX según sea necesario
    console.log('Searching for:', query);
    
    // Ejemplo de implementación con fetch
    /*
    fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            displaySearchResults(data.results);
        })
        .catch(error => {
            console.error('Error en búsqueda:', error);
        });
    */
}

/**
 * Limpiar resultados de búsqueda
 */
function clearSearchResults() {
    const resultsContainer = document.querySelector('.search-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = '';
        resultsContainer.style.display = 'none';
    }
}

/**
 * Inicializar botones de exportación
 */
function initializeExportButtons() {
    const exportButtons = document.querySelectorAll('.btn-export, [data-export]');
    
    exportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Mostrar indicador de carga
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Exportando...';
            this.disabled = true;
            
            // Restaurar después de 3 segundos (tiempo estimado de exportación)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 3000);
        });
    });
}

/**
 * Animaciones de entrada
 */
function initializeAnimations() {
    // Animar elementos al hacer scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observar cartas y elementos principales
    const animateElements = document.querySelectorAll('.card, .alert, .table-responsive');
    animateElements.forEach(el => {
        observer.observe(el);
    });
}

/**
 * Utilidades generales
 */

// Mostrar notificación toast
function showToast(message, type = 'info') {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Crear container si no existe
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Agregar toast
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Inicializar y mostrar
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Limpiar después de ocultar
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Confirmar acción con modal personalizado
function confirmAction(title, message, callback) {
    const modalHtml = `
        <div class="modal fade" id="confirmModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" class="btn btn-primary" id="confirmBtn">Confirmar</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remover modal existente si hay uno
    const existingModal = document.querySelector('#confirmModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Agregar nuevo modal
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    const modal = new bootstrap.Modal(document.querySelector('#confirmModal'));
    
    // Manejar confirmación
    document.querySelector('#confirmBtn').addEventListener('click', function() {
        callback();
        modal.hide();
    });
    
    // Limpiar al cerrar
    document.querySelector('#confirmModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
    
    modal.show();
}

// Formatear números para visualización
function formatNumber(num, decimals = 0) {
    return new Intl.NumberFormat('es-CO', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(num);
}

// Formatear moneda
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(amount);
}

// Copiar texto al portapapeles
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copiado al portapapeles', 'success');
    } catch (err) {
        console.error('Error al copiar:', err);
        showToast('Error al copiar', 'danger');
    }
}

// Validar archivo antes de subir
function validateFile(file, allowedTypes = [], maxSizeMB = 5) {
    const errors = [];
    
    // Validar tipo
    if (allowedTypes.length > 0) {
        const fileType = file.type;
        const isValidType = allowedTypes.some(type => {
            if (type.includes('*')) {
                return fileType.startsWith(type.replace('*', ''));
            }
            return fileType === type;
        });
        
        if (!isValidType) {
            errors.push(`Tipo de archivo no permitido. Permitidos: ${allowedTypes.join(', ')}`);
        }
    }
    
    // Validar tamaño
    const fileSizeMB = file.size / 1024 / 1024;
    if (fileSizeMB > maxSizeMB) {
        errors.push(`El archivo es muy grande. Máximo permitido: ${maxSizeMB}MB`);
    }
    
    return errors;
}

// Auto-resize de textareas
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Inicializar auto-resize para todos los textareas
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
        
        // Trigger inicial
        autoResizeTextarea(textarea);
    });
});

// Exportar funciones globales para uso en templates
window.RRHHPro = {
    showToast,
    confirmAction,
    formatNumber,
    formatCurrency,
    copyToClipboard,
    validateFile
};