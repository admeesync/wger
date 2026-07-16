import os
import urllib.request
import urllib.error
from settings.settings import settings

class StorageService:
    def __init__(self):
        self.supabase_enabled = False
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_key
        self.bucket_name = settings.supabase_bucket_name

        if self.supabase_url and self.supabase_key and self.bucket_name:
            self.supabase_url = self.supabase_url.rstrip('/')
            self.supabase_enabled = True

    def upload_file(self, file_data: bytes, filename: str) -> str:
        """
        Uploads file data and returns the filename/key.
        """
        if self.supabase_enabled:
            ext = os.path.splitext(filename)[1].lower()
            content_type = "image/jpeg"
            if ext == ".png":
                content_type = "image/png"
            elif ext == ".gif":
                content_type = "image/gif"
            elif ext == ".webp":
                content_type = "image/webp"

            url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}"
            req = urllib.request.Request(
                url=url,
                data=file_data,
                headers={
                    "Authorization": f"Bearer {self.supabase_key}",
                    "Content-Type": content_type
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(req) as response:
                    response.read()
                return filename
            except Exception as e:
                print(f"Failed to upload to Supabase, falling back to local: {e}")

        # Local fallback
        os.makedirs(settings.upload_dir, exist_ok=True)
        file_path = os.path.join(settings.upload_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file_data)
        return filename

    def delete_file(self, filename: str):
        """
        Deletes a file by its filename/key.
        """
        if self.supabase_enabled:
            url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{filename}"
            req = urllib.request.Request(
                url=url,
                headers={
                    "Authorization": f"Bearer {self.supabase_key}"
                },
                method="DELETE"
            )
            try:
                with urllib.request.urlopen(req) as response:
                    response.read()
                return
            except Exception as e:
                print(f"Failed to delete from Supabase, trying local: {e}")

        # Local fallback delete
        file_path = os.path.join(settings.upload_dir, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Failed to delete local file {file_path}: {e}")

    def get_file_url(self, filename: str) -> str:
        """
        Returns the URL to access the file.
        """
        if not filename:
            return ""
            
        if self.supabase_enabled:
            return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"
        else:
            return f"/uploads/{filename}"

storage_service = StorageService()
