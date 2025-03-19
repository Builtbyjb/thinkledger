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
            joinWaitlistBtns.forEach((btn) => {
                btn.classList.remove("hidden");
            });
            joinWaitlistForms.forEach((form) => {
                form.classList.add("hidden");
            });
        });
    });
})();
