(function () {
    const emailJsPublicKey = "o25JYcOD9t6qyLJvg";
    const emailJsServiceID = "service_8ve3b9t";
    const emailJsTemplateId = "template_joq4eek";

    emailjs.init({ publicKey: emailJsPublicKey });

    const faqItems = document.querySelectorAll(".faq-item");
    faqItems.forEach((item) => {
        const btn = item.querySelector("button");
        btn.addEventListener("click", () => {
            const expanded = "true" === btn.getAttribute("aria-expanded");
            faqItems.forEach((otherItem) => {
                otherItem !== item &&
                    (otherItem.classList.remove("active"),
                    otherItem
                        .querySelector("button")
                        .setAttribute("aria-expanded", "false"));
            }),
                item.classList.toggle("active"),
                btn.setAttribute("aria-expanded", !expanded);
        });
    }),
        document
            .querySelector("#contact-form-submit")
            .addEventListener("click", async () => {
                const name = document.querySelector("#contact-form-name").value;
                const email = document.querySelector(
                    "#contact-form-email",
                ).value;
                const subject = document.querySelector(
                    "#contact-form-subject",
                ).value;
                const description = document.querySelector(
                    "#contact-form-description",
                ).value;
                const privacyPolicy = document.querySelector(
                    "#contact-form-privacy-policy",
                );
                if (privacyPolicy.checked) {
                    const formData = new FormData();
                    formData.append("name", name),
                        formData.append("email", email),
                        formData.append("subject", subject),
                        formData.append("description", description);
                    try {
                        const response = await emailjs.send(
                            emailJsServiceID,
                            emailJsTemplateId,
                            Object.fromEntries(formData),
                        );
                        if (response.status === 200) {
                            alert(
                                "Your email has been sent, we will get back to shortly",
                            );
                        } else {
                            alert(
                                "An error occurred while sending your email, Please try again",
                            );
                        }
                    } catch (error) {
                        console.log(error);
                    }
                    return;
                }
                document.querySelector(
                    "#contact-form-privacy-policy-error",
                ).innerText =
                    "Before sending an emai, please review and agree to our privacy policy";
            });
})();
