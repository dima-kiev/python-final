import cloudinary
import cloudinary.uploader
from fastapi import UploadFile


class UploadFileService:
    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """
        Initialize a UploadFileService.

        Args:
            cloud_name (str): Cloudinary's cloud name.
            api_key (str): Cloudinary's API key.
            api_secret (str): Cloudinary's API secret.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file: UploadFile, username: str) -> str:
        """
        Upload file to the Cloudinary for the User with `username`.

        Args:
            file (UploadFile): The file to upload to Cloudinary.
            username (str): The User's username.

        Returns:
            str: The URL of the uploaded file.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
