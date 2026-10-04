use anyhow::{Context, Result, bail};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::{Component, Path, PathBuf};
use std::time::{SystemTime, UNIX_EPOCH};

pub fn identifier(prefix: &str) -> String {
    format!(
        "{prefix}-{}",
        &uuid::Uuid::new_v4().simple().to_string()[..16]
    )
}

pub fn token() -> String {
    format!(
        "{}{}",
        uuid::Uuid::new_v4().simple(),
        uuid::Uuid::new_v4().simple()
    )
}

pub fn now() -> String {
    chrono::Utc::now().format("%Y-%m-%dT%H:%M:%SZ").to_string()
}

pub fn seconds() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}

pub fn digest(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

pub fn string<'a>(value: &'a Value, field: &str) -> Result<&'a str> {
    value
        .get(field)
        .and_then(Value::as_str)
        .filter(|s| !s.is_empty())
        .with_context(|| format!("{field} must be a nonempty string."))
}

pub fn json(path: &Path) -> Result<Value> {
    Ok(serde_json::from_slice(
        &fs::read(path).with_context(|| format!("Read {}", path.display()))?,
    )?)
}

pub fn atomic_json(path: &Path, value: &Value) -> Result<()> {
    let bytes = serde_json::to_vec_pretty(value)?;
    atomic_write(path, &[bytes.as_slice(), b"\n"].concat(), true)
}

pub fn atomic_write(path: &Path, bytes: &[u8], private: bool) -> Result<()> {
    let parent = path.parent().context("File needs a parent directory.")?;
    fs::create_dir_all(parent)?;
    let temporary = parent.join(format!(
        ".{}.{}.tmp",
        path.file_name()
            .context("Missing filename.")?
            .to_string_lossy(),
        identifier("write")
    ));
    let result = (|| -> Result<()> {
        let mut options = OpenOptions::new();
        options.write(true).create_new(true);
        #[cfg(unix)]
        {
            use std::os::unix::fs::OpenOptionsExt;
            options.mode(if private { 0o600 } else { 0o644 });
        }
        let mut file = options.open(&temporary)?;
        file.write_all(bytes)?;
        file.sync_all()?;
        if !private && path.exists() {
            fs::set_permissions(&temporary, fs::metadata(path)?.permissions())?;
        }
        fs::rename(&temporary, path)?;
        Ok(())
    })();
    let _ = fs::remove_file(&temporary);
    result
}

pub fn project_path(project: &Path, relative: &str) -> Result<PathBuf> {
    let value = Path::new(relative);
    if relative.is_empty()
        || relative.contains('\\')
        || value.is_absolute()
        || value
            .components()
            .any(|part| matches!(part, Component::ParentDir | Component::Prefix(_)))
    {
        bail!("Expected a bounded project-relative path: {relative}");
    }
    let candidate = project.join(value);
    let mut existing = candidate.as_path();
    while !existing.exists() {
        if fs::symlink_metadata(existing).is_ok() {
            bail!("Dangling installation path: {relative}");
        }
        existing = existing.parent().context("Path has no existing parent.")?;
    }
    if !existing.canonicalize()?.starts_with(project) {
        bail!("Path escapes the project: {relative}");
    }
    Ok(candidate)
}

pub fn discover_project(explicit: Option<&Path>) -> Result<PathBuf> {
    if let Some(path) = explicit {
        return Ok(path.canonicalize()?);
    }
    if let Some(path) = std::env::var_os("OKMS_PROJECT") {
        return Ok(PathBuf::from(path).canonicalize()?);
    }
    let current = std::env::current_dir()?;
    if let Some(root) = current
        .ancestors()
        .find(|path| path.join(".okms/team.json").is_file())
    {
        return Ok(root.to_path_buf());
    }
    if let Ok(executable) = std::env::current_exe()
        && let Some(root) = executable.parent().and_then(Path::parent)
        && root.join(".okms/team.json").is_file()
    {
        return Ok(root.canonicalize()?);
    }
    Ok(current)
}

pub fn shell_quote(value: &str) -> String {
    format!("'{}'", value.replace('\'', "'\\''"))
}
