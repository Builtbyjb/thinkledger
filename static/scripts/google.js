import { setActiveLink, handleSidebar } from "./utils.min.js";

(function () {
    setActiveLink();
    handleSidebar();

    const connectGoogleServicesForm = document.querySelector(
        "#connect-google-services-form",
    );

    // connectGoogleServicesForm.addEventListener("submit", async (event) => {
    //     event.preventDefault();

    //     const googleSheetValue = event.target.googlesheet.checked;
    //     const googleDriveValue = event.target.googledrive.checked;

    //     try {
    //         const response = await fetch(
    //             `/auth-google-service?google_sheet=${googleSheetValue}&google_drive=${googleDriveValue}`,
    //         );

    //         if (response.status === 200) {
    //             window.location.replace(response.url);
    //         } else {
    //             const data = await response.json();
    //             console.log(data);
    //         }
    //     } catch (error) {
    //         console.log(error);
    //     }
    // });
})();
