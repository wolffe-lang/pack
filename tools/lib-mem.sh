# lib-mem.sh — sourced; RULES section 4's gate for a heavy job on a Mac
# (nomad): proceed only with 8 GB free, inactive and speculative together,
# read from vm_stat by the script itself, never by eye. A Linux host passes.
require_memory() {
    [ "$(uname -s)" = Darwin ] || return 0
    free=$(vm_stat | awk '/page size of/ {gsub("[^0-9]","",$8); page=$8} /Pages (free|inactive|speculative)/ {gsub("\\.","",$NF); s+=$NF} END {printf "%d", s*page/1073741824}')
    if [ "$free" -lt 8 ]; then
        echo "${0##*/}: REFUSED on this Mac: ${free} GB free+inactive+speculative, the floor is 8 GB (RULES section 4)" >&2
        exit 3
    fi
}
