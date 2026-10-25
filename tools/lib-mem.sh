# lib-mem.sh — sourced; RULES section 4's gate for a heavy job on nomad (the
# maintainer's Mac): proceed only with 8 GB free, inactive and speculative
# together, read from vm_stat by the script itself, never by eye. The gate
# applies only on nomad (hostname, or PACK_LANE_HOST=nomad) and only while
# PACK_MEMORY_GATE is not 0: GitHub's macOS runner reads a free figure that
# means nothing for it, so the workflow's macOS job sets PACK_MEMORY_GATE=0.
# tools/memgate.py is the same decision for the Python tools, and
# ci/memgate-test.py holds both to it.
require_memory() {
    [ "$(uname -s)" = Darwin ] || return 0
    [ "${PACK_MEMORY_GATE:-1}" != 0 ] || return 0
    host=${PACK_LANE_HOST:-$(hostname -s 2>/dev/null || uname -n)}
    case "$(printf '%s' "$host" | tr 'A-Z' 'a-z')" in
    nomad | nomad.*) ;;
    *) return 0 ;;
    esac
    free=$(vm_stat | awk '/page size of/ {gsub("[^0-9]","",$8); page=$8} /Pages (free|inactive|speculative)/ {gsub("\\.","",$NF); s+=$NF} END {printf "%d", s*page/1073741824}')
    if [ "$free" -lt 8 ]; then
        echo "${0##*/}: REFUSED on nomad: ${free} GB free+inactive+speculative, the floor is 8 GB (RULES section 4)" >&2
        exit 3
    fi
}
