package handlers

import (
	templates "server/templates/guest"

	"github.com/gofiber/fiber/v2"
)

func (h *Handler) Index(c *fiber.Ctx) error {
	return Render(c, templates.IndexPage())
}

func (h *Handler) Support(c *fiber.Ctx) error {
	return Render(c, templates.SupportPage())
}

func (h *Handler) SupportBookkeeping(c *fiber.Ctx) error {
	return Render(c, templates.SupportBookkeepingPage())
}

func (h *Handler) SupportFinancialReports(c *fiber.Ctx) error {
	return Render(c, templates.SupportFinancialReportsPage())
}

func (h *Handler) SupportAnalyticsInsights(c *fiber.Ctx) error {
	return Render(c, templates.SupportAnalyticsInsightsPage())
}

func (h *Handler) PrivacyPolicy(c *fiber.Ctx) error {
	return Render(c, templates.PrivacyPolicyPage())
}

func (h *Handler) TermsOfService(c *fiber.Ctx) error {
	return Render(c, templates.TermsOfServicePage())
}
