pub mod adoption;
pub mod cli;
pub mod gitops;
pub mod process;
pub mod providers;
pub mod runtime;
pub mod state;
pub mod util;
pub mod worker;

pub const VERSION: &str = env!("CARGO_PKG_VERSION");
