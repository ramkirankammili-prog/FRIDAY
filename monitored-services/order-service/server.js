const express = require("express");

const app = express();

const PORT = 3001;

app.get("/", (req, res) => {
    res.json({
        service: "Order Service",
        status: "running",
        message: "Order service is alive"
    });
});

app.get("/orders", (req, res) => {
    res.json({
        service: "Order Service",
        orders: 5
    });
});

app.get("/health", (req, res) => {
    res.json({
        service: "Order Service",
        status: "healthy"
    });
});

app.listen(PORT, () => {
    console.log(`Order Service running on http://localhost:${PORT}`);
});