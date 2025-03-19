package handlers

import (
	"encoding/json"
	"fmt"
	"log"
	"os"

	"github.com/gofiber/fiber/v2"
	"github.com/sendgrid/sendgrid-go"
)

type Contact struct {
	Firstname string `json:"firstname"`
	Lastname  string `json:"lastname"`
	Email     string `json:"email"`
}

type ContactRequest struct {
	ListIds  []string  `json:"list_ids"`
	Contacts []Contact `json:"contacts"`
}

func (h *Handler) JoinWaitlist(c *fiber.Ctx) error {

	var contact Contact

	if err := c.BodyParser(&contact); err != nil {
		log.Println("Could not parse contact")
		return c.SendStatus(fiber.StatusBadRequest)
	}

	sendGridApiKey := os.Getenv("SENDGRID_API_KEY")
	sendGridListId := os.Getenv("SENDGRID_LIST_ID")

	data := ContactRequest{
		ListIds: []string{sendGridListId},
		Contacts: []Contact{
			{
				Firstname: contact.Firstname,
				Lastname:  contact.Lastname,
				Email:     contact.Email,
			},
		},
	}

	fmt.Println(data)

	jsonBytes, err := json.Marshal(data)
	if err != nil {
		log.Println("failed to json marshal contacts")
		return c.SendStatus(fiber.StatusInternalServerError)
	}

	sendGridUrl := "https://api.sendgrid.com"
	request := sendgrid.GetRequest(sendGridApiKey, "/v3/marketing/contacts", sendGridUrl)
	request.Method = "PUT"
	request.Body = jsonBytes

	response, err := sendgrid.API(request)
	if err != nil {
		log.Println("Sendgrid api error")
		return c.SendStatus(fiber.StatusInternalServerError)
	}

	if response.StatusCode != 202 {
		log.Println(response.Body)
		return c.SendStatus(fiber.StatusInternalServerError)
	}

	log.Println(response.Body)
	log.Println("Contact saved!!")
	return c.SendStatus(fiber.StatusOK)
}
