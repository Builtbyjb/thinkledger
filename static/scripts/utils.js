export function setActiveLink() {
    const path = window.location.pathname.slice(1);
    // console.log(path);

    document.querySelectorAll(".link").forEach((element) => {
        if (element.id === path) {
            element.classList.add("bg-gray-600/50", "rounded-lg");
        } else {
            element.classList.remove("bg-gray-600/50", "rounded-lg");
        }
    });
}
