FROM golang:1.24.1-alpine3.21

# set working directory
WORKDIR /app

# Install air for hot reload
RUN go install github.com/air-verse/air@latest

# Install temple for templating
RUN go install github.com/a-h/templ/cmd/templ@latest

# Copies local files to the docker container
COPY . .

RUN go mod tidy

# Ensure air binary is in the path
ENV PATH="/go/bin:${PATH}"

RUN go build -o ./cmd/main ./cmd/main.go

EXPOSE 3000

CMD ["./cmd/main"]
