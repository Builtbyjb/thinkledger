import { setActiveLink, handleSidebar } from "./utils.min.js";

document.addEventListener("DOMContentLoaded", () => {
  setActiveLink();
  handleSidebar();

  const connectGoogleServicesForm = document.querySelector("#connect-google-services-form");
  connectGoogleServicesForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const googleSheetValue = event.target.googlesheet.checked;
    const googleDriveValue = event.target.googledrive.checked;

    try {
      const response = await fetch(
        `/google/services?google_sheet=${googleSheetValue}&google_drive=${googleDriveValue}`,
      );
      const data = await response.json();
      if (response.status === 200) {
        window.location.replace(data.url);
      } else {
        console.log(data);
      }
    } catch (error) {
      console.log(error);
    }
  });
});
