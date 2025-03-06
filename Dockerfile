FROM golang:1.23.5

# set working directory
WORKDIR /app/server

# Install air for hot reload
RUN go install github.com/air-verse/air@latest

# Copies local files to the docker container
COPY . .

RUN go mod tidy

# Ensure air binary is in the path
ENV PATH="/go/bin:${PATH}"

RUN go build -o ./cmd/main ./cmd/main.go

EXPOSE 3000

CMD ["./cmd/main"]