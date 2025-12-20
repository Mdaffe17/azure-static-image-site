const FUNCTION_APP_URL = "https://func-static-image-site-hpd7a2drg4hkdgcr.canadaeast-01.azurewebsites.net/api"; 

async function uploadImage() {
  const fileInput = document.getElementById("fileInput");
  if (fileInput.files.length === 0) {
    alert("Veuillez sélectionner une image");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const response = await fetch(`${FUNCTION_APP_URL}/upload_image`, {
    method: "POST",
    body: formData
  });

  if (response.ok) {
    alert("Image téléversée avec succès");
  } else {
    alert("Erreur lors du téléversement");
  }
}

async function loadImages() {
  const response = await fetch(`${FUNCTION_APP_URL}/list_images`);
  const images = await response.json();

  const gallery = document.getElementById("gallery");
  gallery.innerHTML = "";

  images.forEach(url => {
    const img = document.createElement("img");
    img.src = url;
    gallery.appendChild(img);
  });
}
