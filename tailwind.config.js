/** @type {import('tailwindcss').config} */

export default {
    content: ["./templates/**/*.templ"],
    theme: {
        extend: {
            fontFamily: {
                outfit: ["Outfit", "sans-serif"],
                poppins: ["Poppins", "sans-serif"],
            },
            colors: {
                primary: "#0A0A0A",
                accent: "#0065F2",
            },
        },
    },
    plugins: [require("tailwindcss-animate")],
};
