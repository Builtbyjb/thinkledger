package handlers

import (
	"net/http"
	"server/templates"
	"server/templates/auth"
	"server/templates/guest"

	"github.com/labstack/echo/v4"
)

func (h *Handler) Index(c echo.Context) error {
	return Render(c, http.StatusOK, guest.IndexPage())
}

func (h *Handler) Support(c echo.Context) error {
	return Render(c, http.StatusOK, guest.SupportPage())
}

func (h *Handler) SupportBookkeeping(c echo.Context) error {
	return Render(c, http.StatusOK, guest.SupportBookkeepingPage())
}

func (h *Handler) SupportFinancialReports(c echo.Context) error {
	return Render(c, http.StatusOK, guest.SupportFinancialReportsPage())
}

func (h *Handler) SupportAnalyticsInsights(c echo.Context) error {
	return Render(c, http.StatusOK, guest.SupportAnalyticsInsightsPage())
}

func (h *Handler) PrivacyPolicy(c echo.Context) error {
	return Render(c, http.StatusOK, guest.PrivacyPolicyPage())
}

func (h *Handler) TermsOfService(c echo.Context) error {
	return Render(c, http.StatusOK, guest.TermsOfServicePage())
}

func (h *Handler) NotFound(c echo.Context) error {
	return Render(c, http.StatusOK, templates.NotFoundPage())
}

func (h *Handler) SignIn(c echo.Context) error {
	return Render(c, http.StatusOK, templates.SignInPage())
}

func (h *Handler) Home(c echo.Context) error {
	return Render(c, http.StatusOK, auth.HomePage())
}
