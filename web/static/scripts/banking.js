import { setActiveLink, handleSidebar } from "./utils.min.js";

(function () {
  setActiveLink();
  handleSidebar();

  const connectBankBtn = document.querySelector("#connect-bank-account");

  // Get plaid link token
  connectBankBtn.addEventListener("click", async () => {
    try {
      const response = await fetch("/plaid/link-token", {method: "GET"});
      const data = await response.json();
      const linkToken = data.linkToken;
      // Get plaid access token
      if (response.status === 200) {
        const handler = Plaid.create({
          token: linkToken,
          onSuccess: async (public_token, metadata) => {
            console.log("Account metadata: ", metadata.accounts);
            console.log("Institution metadata: ", metadata.institution);
            try {
              const response = await fetch("/plaid/access-token", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                  public_token: public_token,
                  accounts: metadata.accounts,
                  institution: metadata.institution,
                }),
              });

              const data = await response.json();
              console.log(data);
            } catch (error) {
              console.log(error);
            }
          },
          onLoad: () => {},
          onExit: (err, metadata) => {},
          onEvent: (eventName, metadata) => {},
        });
        handler.open();
      }
    } catch (error) {
      console.log(error);
    }
  });
})();
