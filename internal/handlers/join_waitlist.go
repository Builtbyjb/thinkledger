package handlers

import (
	"encoding/json"
	"log"
	"net/http"
	"os"

	"github.com/labstack/echo/v4"
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

func (h *Handler) JoinWaitlist(c echo.Context) error {

	// Simple validation
	if len(c.FormValue("firstname")) == 0 {
		c.NoContent(400)
	}

	if len(c.FormValue("lastname")) == 0 {
		c.NoContent(400)
	}

	if len(c.FormValue("email")) == 0 {
		c.NoContent(400)
	}

	sendGridApiKey := os.Getenv("SENDGRID_API_KEY")
	sendGridListId := os.Getenv("SENDGRID_LIST_ID")

	data := ContactRequest{
		ListIds: []string{sendGridListId},
		Contacts: []Contact{
			{
				Firstname: c.FormValue("firstname"),
				Lastname:  c.FormValue("lastname"),
				Email:     c.FormValue("email"),
			},
		},
	}

	// fmt.Println(data)

	jsonBytes, err := json.Marshal(data)
	if err != nil {
		log.Println("failed to json marshal contacts")
		return c.NoContent(http.StatusInternalServerError)
	}

	sendGridUrl := "https://api.sendgrid.com"
	request := sendgrid.GetRequest(sendGridApiKey, "/v3/marketing/contacts", sendGridUrl)
	request.Method = "PUT"
	request.Body = jsonBytes

	response, err := sendgrid.API(request)
	if err != nil {
		log.Println("Sendgrid api error")
		return c.NoContent(http.StatusInternalServerError)
	}

	if response.StatusCode != 202 {
		log.Println(response.Body)
		return c.NoContent(http.StatusInternalServerError)
	}

	log.Println(response.Body)
	log.Println("Contact saved!!")
	return c.NoContent(http.StatusOK)
}
