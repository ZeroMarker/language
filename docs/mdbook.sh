mise use -g rust

cargo install mdbook

mdbook init

python generate_summary.py

mdbook build

mdbook serve
