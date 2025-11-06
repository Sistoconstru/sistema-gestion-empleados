from storages.backends.s3boto3 import S3Boto3Storage

class MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False

    def _save(self, name, content):
        import logging
        logger = logging.getLogger('storages')
        logger.info(f"Guardando archivo en S3: {name}")
        return super()._save(name, content)
