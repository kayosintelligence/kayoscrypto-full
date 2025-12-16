use axum::{routing::get, Router};
use kayoscrypto_safe::KayosCryptoSafe;
use serde::Serialize;
use std::net::SocketAddr;
use tracing::info;

#[derive(Serialize)]
struct HealthCheck {
    status: &'static str,
}

async fn health() -> axum::Json<HealthCheck> {
    axum::Json(HealthCheck { status: "ok" })
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    // Placeholder: initialize core engine for future use.
    let _core = KayosCryptoSafe::new();

    let app = Router::new().route("/health", get(health));

    let addr: SocketAddr = "0.0.0.0:8080".parse().expect("valid socket");
    info!(%addr, "starting kayoscrypto server");

    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .expect("server failed");
}
