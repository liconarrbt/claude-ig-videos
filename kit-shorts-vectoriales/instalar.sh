#!/bin/zsh
# Instalador del kit de shorts vectoriales.
#   ./instalar.sh              verifica requisitos, registra los MCP e instala las skills
#   ./instalar.sh --descargar  además descarga las CLIs de ArtCraft que falten (GitHub storytold/*)
set -euo pipefail

KIT="${0:A:h}"
APPS="${CRAFT_CLI_DIR:-$HOME/Applications/craft-cli}"
TRABAJO="${CARPETA_TRABAJO:-$HOME/Documents/Artcarft/proyectos}"
EQUIPO="DJ6XS33FX8"   # Learning Machines LLC (firma de todas las apps de ArtCraft)
DESCARGAR=0; [[ "${1:-}" == "--descargar" ]] && DESCARGAR=1
typeset -A VERSION=(photocraft 0.10.0 vectorcraft 0.13.1 effectcraft 0.11.1 filmcraft 0.9.0 soundcraft 0.5.0)
ok()  { print -P "%F{green}✔%f $1" }
mal() { print -P "%F{red}✘%f $1" }
av()  { print -P "%F{yellow}!%f $1" }
FALTAN=0

print "\n== Sistema"
[[ "$(uname)" == "Darwin" ]] && ok "macOS $(sw_vers -productVersion)" || { mal "Este kit está probado en macOS"; FALTAN=1; }
command -v python3 >/dev/null && ok "$(python3 --version)" || { mal "Falta python3 (instálalo con Homebrew: brew install python)"; FALTAN=1; }
command -v afinfo >/dev/null && ok "afinfo (incluido en macOS)" || { mal "Falta afinfo"; FALTAN=1; }
[[ -e "/System/Library/Fonts/Avenir Next Condensed.ttc" ]] && ok "Fuente Avenir Next Condensed" || av "No encuentro Avenir Next Condensed: cambia 'fuente' en escenas.json → estilo"

print "\n== CLIs de ArtCraft ($APPS)"
for app in photocraft vectorcraft effectcraft filmcraft soundcraft; do
  bin=$(ls -d "$APPS/$app"/$app-cli-*/$app-cli(N) 2>/dev/null | tail -1)
  if [[ -z "$bin" && $DESCARGAR == 1 ]]; then
    v=${VERSION[$app]}; zip="$app-cli-$v-macos-universal.zip"
    mkdir -p "$APPS/$app/_descarga"
    print "  descargando $zip …"
    curl -fsSL -o "$APPS/$app/_descarga/$zip" "https://github.com/storytold/$app/releases/download/v$v/$zip"
    unzip -q -o "$APPS/$app/_descarga/$zip" -d "$APPS/$app"
    bin="$APPS/$app/$app-cli-$v-macos-universal/$app-cli"
  fi
  if [[ -z "$bin" ]]; then
    mal "$app-cli no instalado → ./instalar.sh --descargar  (o https://getartcraft.com/apps/$app)"; FALTAN=1; continue
  fi
  firma=$(codesign -dv "$bin" 2>&1 | grep TeamIdentifier || true)
  notar=$(spctl --assess --type install -vv "$bin" 2>&1 | grep -c "Notarized Developer ID" || true)
  if [[ "$firma" == *"$EQUIPO"* && "$notar" -ge 1 ]]; then
    ok "$app-cli $("$bin" --version 2>&1 | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1) (firmado y notarizado)"
  else
    mal "$bin no tiene la firma esperada de $EQUIPO: no lo uses"; FALTAN=1
  fi
done

print "\n== Fish Audio"
if [[ -n "${FISHAUDIO_API_KEY:-}" ]] || grep -q "FISHAUDIO_API_KEY" ~/.zshrc 2>/dev/null || grep -qs "^FISHAUDIO_API_KEY=" "$(dirname "$0")/../.env"; then
  ok "FISHAUDIO_API_KEY configurada"
else
  av "Falta FISHAUDIO_API_KEY → crea una en https://fish.audio/app/api-keys y añade a ~/.zshrc:"
  print "     export FISHAUDIO_API_KEY=\"tu_clave\""
fi

print "\n== Servidores MCP (~/.claude.json)"
if [[ -f ~/.claude.json ]]; then
  cp ~/.claude.json ~/.claude.json.bak-kit-shorts
  python3 -I - "$APPS" "$TRABAJO" <<'EOF'
import glob, json, os, sys
apps, trabajo = sys.argv[1], sys.argv[2]
p = os.path.expanduser("~/.claude.json"); d = json.load(open(p)); s = d.setdefault("mcpServers", {})
raices = ["--automation-read-root", trabajo, "--automation-write-root", trabajo]
extra = {"photocraft": raices, "vectorcraft": raices, "effectcraft": ["--autosave", *raices]}
for app in ["photocraft", "vectorcraft", "effectcraft", "filmcraft", "soundcraft"]:
    b = sorted(glob.glob(f"{apps}/{app}/{app}-cli-*/{app}-cli"))
    if b:
        s[app] = {"type": "stdio", "command": b[-1], "args": ["mcp", *extra.get(app, [])], "env": {}}
        print(f"  ✔ {app}")
json.dump(d, open(p, "w"), indent=2)
EOF
  mkdir -p "$TRABAJO"
  ok "MCP registrados (copia de seguridad: ~/.claude.json.bak-kit-shorts). Carpeta de trabajo: $TRABAJO"
else
  av "No existe ~/.claude.json (abre Claude Code una vez y vuelve a correr el instalador)"
fi

print "\n== Skills (~/.claude/skills)"
mkdir -p ~/.claude/skills
for s in "$KIT"/skills/*(/); do
  n=${s:t}; dest=~/.claude/skills/$n
  if [[ -L "$dest" || ! -e "$dest" ]]; then ln -sfn "$s" "$dest"; ok "$n"; else av "$dest ya existe y no es un enlace: no lo toco"; fi
done

print ""
(( FALTAN )) && mal "Faltan requisitos (arriba en rojo)." || ok "Todo listo. Abre una sesión nueva de Claude para que carguen los MCP y las skills."
