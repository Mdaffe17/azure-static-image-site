import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from PIL import Image
import io
import json
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




@app.blob_trigger(arg_name="myblob", path="images-original/{name}",
                               connection="AzureWebJobsStorage") 
def resize_image(myblob: func.InputStream):
    logging.info(f"Redimensionnement de l'image : {myblob.name}")

    image_bytes = myblob.read()
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")

    image.thumbnail((256, 256))

    output = io.BytesIO()
    image.save(output, format="JPEG")
    output.seek(0)

    connection_string = os.getenv("AzureWebJobsStorage")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    filename = os.path.basename(myblob.name)

    container_client = blob_service_client.get_container_client("images-thumbnails")
    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(output, overwrite=True)

    logging.info(f"Miniature créée : {filename}")

# This example uses SDK types to directly access the underlying BlobClient object provided by the Blob storage trigger.
# To use, uncomment the section below and add azurefunctions-extensions-bindings-blob to your requirements.txt file
# Ref: aka.ms/functions-sdk-blob-python
#
# import azurefunctions.extensions.bindings.blob as blob
# @app.blob_trigger(arg_name="client", path="images-original/{name}",
#                   connection="AzureWebJobsStorage")
# def resize_image(client: blob.BlobClient):
#     logging.info(
#         f"Python blob trigger function processed blob \n"
#         f"Properties: {client.get_blob_properties()}\n"
#         f"Blob content head: {client.download_blob().read(size=1)}"
#     )


@app.route(route="list_images", auth_level=func.AuthLevel.ANONYMOUS)
def list_images(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fonction list_images appelée")

    try:
        connection_string = os.getenv("AzureWebJobsStorage")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        container_name = "images-thumbnails"
        container_client = blob_service_client.get_container_client(container_name)

        images = []

        for blob in container_client.list_blobs():
            blob_url = (
                f"https://{blob_service_client.account_name}.blob.core.windows.net/"
                f"{container_name}/{blob.name}"
            )
            images.append(blob_url)

        return func.HttpResponse(
            body=json.dumps(images),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(
            "Erreur lors de la récupération des images",
            status_code=500
        )