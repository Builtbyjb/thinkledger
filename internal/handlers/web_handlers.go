package handlers

import (
	"server/templates"
	"server/templates/auth"
	"server/templates/guest"

	"github.com/labstack/echo/v4"
)

func checkAuth(c echo.Context) bool {
	cookie, err := c.Request().Cookie("session_id")
	if err != nil {
		return false
	}

	if cookie.Value == "" {
		return false
	}

	return true
}

func (h *Handler) Index(c echo.Context) error {

	// Redirect users to the home page if they authenicated
	cookie, err := c.Request().Cookie("session_id")
	if err == nil {

		if cookie.Value != "" {
			c.Redirect(307, "/home")
		}
	}

	return Render(c, 200, guest.IndexPage())
}

func (h *Handler) Support(c echo.Context) error {
	username := c.Get("username").(string)
	isAuth := checkAuth(c)
	return Render(c, 200, guest.SupportPage(isAuth, username))
}

func (h *Handler) SupportBookkeeping(c echo.Context) error {
	username := c.Get("username").(string)
	isAuth := checkAuth(c)
	return Render(c, 200, guest.SupportBookkeepingPage(isAuth, username))
}

func (h *Handler) SupportFinancialReports(c echo.Context) error {
	username := c.Get("username").(string)
	isAuth := checkAuth(c)
	return Render(c, 200, guest.SupportFinancialReportsPage(isAuth, username))
}

func (h *Handler) SupportAnalyticsInsights(c echo.Context) error {
	username := c.Get("username").(string)
	isAuth := checkAuth(c)
	return Render(c, 200, guest.SupportAnalyticsInsightsPage(isAuth, username))
}

func (h *Handler) PrivacyPolicy(c echo.Context) error {
	username := c.Get("username").(string)
	isAuth := checkAuth(c)
	return Render(c, 200, guest.PrivacyPolicyPage(isAuth, username))
}

func (h *Handler) TermsOfService(c echo.Context) error {
	username := c.Get("username").(string)
	isAuth := checkAuth(c)
	return Render(c, 200, guest.TermsOfServicePage(isAuth, username))
}

func (h *Handler) NotFound(c echo.Context) error {
	return Render(c, 200, templates.NotFoundPage())
}

func (h *Handler) SignIn(c echo.Context) error {
	return Render(c, 200, templates.SignInPage())
}

func (h *Handler) Home(c echo.Context) error {
	username := c.Get("username").(string)
	return Render(c, 200, auth.HomePage(username))
}

func (h *Handler) Banking(c echo.Context) error {
	username := c.Get("username").(string)
	return Render(c, 200, auth.BankingPage(username))
}
