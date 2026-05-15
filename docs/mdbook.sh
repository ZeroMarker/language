mise use -g rust

cargo install mdbook
cargo install mdbook-summarizer

mdbook init

mdbook-summarizer --src src

mdbook build

mdbook serve
