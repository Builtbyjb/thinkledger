package gemini

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"server/internal/utils"

	"github.com/google/generative-ai-go/genai"
	"google.golang.org/api/option"
)

func GeminiTrialBalance(prompt string, apiKey string) ([]utils.TrialBalanceEntry, error) {
	ctx := context.Background()

	client, err := genai.NewClient(ctx, option.WithAPIKey(apiKey))
	if err != nil {
		log.Fatalf("Error creating client: %v", err)
	}
	defer client.Close()

	model := client.GenerativeModel("gemini-2.0-flash")
	// model := client.GenerativeModel("gemini-2.0-flash-thinking-exp-01-21")

	model.SetTemperature(1)
	model.SetTopK(40)
	model.SetTopP(0.95)
	model.SetMaxOutputTokens(8192)
	model.ResponseMIMEType = "text/plain"
	// model.SystemInstruction = &genai.Content{
	// 	Parts: []genai.Part{},
	// }

	session := model.StartChat()

	response, err := session.SendMessage(ctx, genai.Text(prompt))
	if err != nil {
		return nil, fmt.Errorf("error sending message: %w", err)
	}

	// TODO: Retrying requests multiple times

	res, err := sanitizeTrialBalanceResponse(response)
	if err != nil {
		return nil, fmt.Errorf("error sanitizing Gemini response: %w", err)
	}

	return res, nil
}

// Sanitize AI Transaction response
func sanitizeTrialBalanceResponse(
	response *genai.GenerateContentResponse,
) ([]utils.TrialBalanceEntry, error) {

	res := response.Candidates[0].Content.Parts[0]

	jsonData, err := json.Marshal(res)
	if err != nil {
		return nil, fmt.Errorf("error marshalling JSON: %w", err)
	}

	jsonString := CleanString(string(jsonData))

	var r []utils.TrialBalanceEntry

	// Unmarshal the cleaned string into the struct
	unMarshalErr := json.Unmarshal([]byte(jsonString), &r)
	if unMarshalErr != nil {
		return nil, fmt.Errorf("error unmarshaling JSON: %w", unMarshalErr)
	}

	return r, nil
}
