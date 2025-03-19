FROM golang:1.24.1-alpine3.21 AS builder
WORKDIR /app
COPY . .
RUN go mod tidy

# Output path first
RUN go build -o ./bin/main.go ./cmd/main.go

FROM golang:1.24.1-alpine3.21
WORKDIR /app
COPY --from=builder /app/static /app/static
COPY --from=builder /app/bin /app/bin
EXPOSE 3000
CMD ["./bin/main.go"]
