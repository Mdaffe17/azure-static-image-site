import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os
import uuid

app = func.FunctionApp()

@app.route(route="upload_image", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def upload_image(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fonction upload_image appelée")

    try:
        file = req.files.get("file")
        if not file:
            return func.HttpResponse(
                "Paramètre 'file' manquant.",
                status_code=400
            )

        if not file.content_type or not file.content_type.startswith("image/"):
            return func.HttpResponse(
                "Le fichier envoyé n'est pas une image.",
                status_code=400
            )

        connection_string = os.getenv("AzureWebJobsStorage")
        if not connection_string:
            return func.HttpResponse(
                "AzureWebJobsStorage non configuré.",
                status_code=500
            )

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_name = "images-original"
        container_client = blob_service_client.get_container_client(container_name)

        extension = os.path.splitext(file.filename)[1]
        blob_name = f"{uuid.uuid4()}{extension}"

        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(file.stream, overwrite=True)

        # Retour unique 
        return func.HttpResponse(
            f"Image téléversée avec succès : {blob_name}",
            status_code=200
        )

    except Exception as e:
        logging.exception("Erreur inattendue dans upload_image")
        return func.HttpResponse(
            f"Erreur serveur : {str(e)}",
            status_code=500
        )
