package gemini

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"server/utils"

	"github.com/google/generative-ai-go/genai"
	"google.golang.org/api/option"
)

func GeminiTransaction(prompt string, apiKey string) (utils.TransactionResponse, error) {
	ctx := context.Background()

	client, err := genai.NewClient(ctx, option.WithAPIKey(apiKey))
	if err != nil {
		log.Fatalf("Error creating client: %v", err)
	}
	defer client.Close()

	// model := client.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")
	model := client.GenerativeModel("gemini-2.0-flash")

	model.SetTemperature(1)
	model.SetTopK(40)
	model.SetTopP(0.95)
	model.SetMaxOutputTokens(8192)
	model.ResponseMIMEType = "text/plain"
	model.SystemInstruction = &genai.Content{
		Parts: []genai.Part{genai.Text(
			fmt.Sprintf(`Your response should be in this format %s. 
      Do not make any assumptions.
	  If the accounts affected is not clear ask for clarification.
	  If the payment method is not clear ask for clarification.
	  If the transaction date is not specified ask for clarification, the data should be in the dd-mm-yyyy format.
	  If the prompt is not related to accounting or tasks an accountant would perform ask for clarification.
	  If more information to record the transaction accurately ask for clarification.
	  `, utils.TransactionResponseFormat),
		)},
	}

	session := model.StartChat()

	response, err := session.SendMessage(ctx, genai.Text(prompt))
	if err != nil {
		return utils.TransactionResponse{}, fmt.Errorf("error sending message: %w", err)
	}

	// TODO: Retrying requests multiple times

	res, err := sanitizeTransactionResponse(response)
	if err != nil {
		return utils.TransactionResponse{}, fmt.Errorf("error sanitizing Gemini response: %w", err)
	}

	return res, nil
}

// Sanitize AI Transaction response
func sanitizeTransactionResponse(
	response *genai.GenerateContentResponse,
) (utils.TransactionResponse, error) {

	res := response.Candidates[0].Content.Parts[0]

	jsonData, err := json.Marshal(res)
	if err != nil {
		return utils.TransactionResponse{}, fmt.Errorf("error marshalling JSON: %w", err)
	}

	jsonString := CleanString(string(jsonData))

	var r utils.TransactionResponse

	// Unmarshal the cleaned string into the struct
	unMarshalErr := json.Unmarshal([]byte(jsonString), &r)
	if unMarshalErr != nil {
		return utils.TransactionResponse{}, fmt.Errorf("error unmarshaling JSON: %w", unMarshalErr)
	}

	return r, nil
}
