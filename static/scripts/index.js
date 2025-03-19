/*
Each form element appears more than onces hence document.querySelectorAll.
Wraping everything in a global function improves minification.
*/

(function () {
    const joinWaitlistBtns = document.querySelectorAll(
        "#display-join-waitlist-form",
    );
    const joinWaitlistForms = document.querySelectorAll("#join-waitlist-form");
    const closeJoinWaitlistBtns = document.querySelectorAll(
        "#close-join-waitlist-form",
    );

    joinWaitlistBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            btn.classList.add("hidden");
            joinWaitlistForms.forEach((form) => {
                form.classList.remove("hidden");
            });
        });
    });

    closeJoinWaitlistBtns.forEach((closeBtn) => {
        closeBtn.addEventListener("click", () => {
            closeJoinWaitlistPopup();
        });
    });

    // Send joinwaitlist email
    document.addEventListener("submit", async (event) => {
        event.preventDefault();
        const elementId = event.target.id;

        if (elementId === "join-waitlist-submit") {
            const firstname = event.target.firstname.value;
            const lastname = event.target.lastname.value;
            const email = event.target.email.value;

            const formData = new FormData();
            formData.append("firstname", firstname);
            formData.append("lastname", lastname);
            formData.append("email", email);

            await addToWaitlist(formData);
        }
    });

    function closeJoinWaitlistPopup() {
        clearForm();

        joinWaitlistBtns.forEach((btn) => {
            btn.classList.remove("hidden");
        });

        joinWaitlistForms.forEach((form) => {
            form.classList.add("hidden");
        });
    }

    // Clears join waitlist form
    function clearForm() {
        const lastnames = document.querySelectorAll("#lastname");
        lastnames.forEach((lastname) => {
            lastname.value = "";
        });

        const firstnames = document.querySelectorAll("#firstname");
        firstnames.forEach((firstname) => {
            firstname.value = "";
        });

        const emails = document.querySelectorAll("#email");
        emails.forEach((email) => {
            email.value = "";
        });
    }

    async function addToWaitlist(formData) {
        try {
            // Send fetch requests
            const response = await fetch(
                "https://thinkledger.app/join-waitlist",
                {
                    method: "POST",
                    body: formData,
                },
            );

            if (response.status === 200) {
                alert(
                    "You've been added to the waitlist! A welcome email has been sent to you. If you don't see it in your inbox, please check your spam folder. Thank you!",
                );
                closeJoinWaitlistPopup();
            } else if (response.status === 400) {
                alert(" Please provide valid credentials");
            }
        } catch (error) {
            console.log(error);
        }
    }
})();
