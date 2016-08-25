DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" #http://stackoverflow.com/questions/59895/can-a-bash-script-tell-which-directory-it-is-stored-in
$1 -t python --verbose "$DIR/../firmware.ksy" --outdir "$DIR/.."
