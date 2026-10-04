use std::fs;
use std::path::{Path, PathBuf};

fn collect(root: &Path, current: &Path, result: &mut Vec<PathBuf>) {
    let mut entries = fs::read_dir(current)
        .expect("Embedded payload directory")
        .map(|e| e.unwrap().path())
        .collect::<Vec<_>>();
    entries.sort();
    for path in entries {
        assert!(
            !path.is_symlink(),
            "Embedded payload must not contain symlinks"
        );
        if path.is_dir() {
            collect(root, &path, result);
        } else if path.extension().is_some_and(|e| e == "md" || e == "toml") {
            result.push(path.strip_prefix(root).unwrap().to_path_buf());
        }
    }
}

fn main() {
    let root = PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").unwrap());
    let profile = root.join("templates/hybrid-team");
    let mut files = Vec::new();
    for directory in ["docs", "native", "skills"] {
        println!("cargo:rerun-if-changed=templates/hybrid-team/{directory}");
        collect(&profile, &profile.join(directory), &mut files);
    }
    let mut source = String::from("pub static PAYLOAD: &[(&str, &[u8])] = &[\n");
    for relative in files {
        let name = relative
            .to_str()
            .expect("UTF-8 payload path")
            .replace('\\', "/");
        let path = profile.join(relative);
        source += &format!(
            "({name:?}, include_bytes!({:?})),\n",
            path.to_str().unwrap()
        );
    }
    source += "];\n";
    let output = PathBuf::from(std::env::var("OUT_DIR").unwrap()).join("payload.rs");
    fs::write(output, source).unwrap();
}
