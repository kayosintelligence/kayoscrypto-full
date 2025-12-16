#!/bin/bash
# Optimizes system environment for accurate timing measurements
# by reducing CPU jitter and scheduling variance.

set -e

echo "🔧 Optimizing environment for timing tests..."
echo "=============================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Warning: Some optimizations require sudo privileges"
    echo "   Run with: sudo ./scripts/optimize_timing_tests.sh"
    echo ""
    echo "   Attempting user-space optimizations only..."
    echo ""
    SUDO_AVAILABLE=false
else
    SUDO_AVAILABLE=true
fi

echo "📊 Setting CPU governor to performance..."
if command -v cpupower &> /dev/null; then
    if [ "$SUDO_AVAILABLE" = true ]; then
        if cpupower frequency-set --governor performance 2>/dev/null; then
            echo "   ✅ CPU governor set to performance"
        else
            echo "   ⚠️  Failed to set CPU governor"
        fi
    else
        echo "   ⚠️  Requires sudo - skipping"
    fi
else
    echo "   ℹ️  cpupower not found - install with: sudo apt install linux-tools-generic"
fi
echo ""

echo "📊 Disabling turbo boost..."
if [ -f /sys/devices/system/cpu/cpufreq/boost ]; then
    if [ "$SUDO_AVAILABLE" = true ]; then
        if echo 0 > /sys/devices/system/cpu/cpufreq/boost; then
            echo "   ✅ Turbo boost disabled"
        else
            echo "   ⚠️  Failed to disable turbo boost"
        fi
    else
        echo "   ⚠️  Requires sudo - skipping"
    fi
elif [ -f /sys/devices/system/cpu/intel_pstate/no_turbo ]; then
    if [ "$SUDO_AVAILABLE" = true ]; then
        if echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo; then
            echo "   ✅ Intel turbo boost disabled"
        else
            echo "   ⚠️  Failed to disable Intel turbo boost"
        fi
    else
        echo "   ⚠️  Requires sudo - skipping"
    fi
else
    echo "   ℹ️  Turbo boost control not available on this system"
fi
echo ""

echo "📊 Current CPU configuration:"
if [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]; then
    GOVERNOR=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
    echo "   Governor: $GOVERNOR"
fi

if [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq ]; then
    FREQ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq)
    FREQ_MHZ=$((FREQ / 1000))
    echo "   Current frequency: ${FREQ_MHZ} MHz"
fi

if [ -f /sys/devices/system/cpu/cpufreq/boost ]; then
    BOOST=$(cat /sys/devices/system/cpu/cpufreq/boost)
    if [ "$BOOST" -eq 0 ]; then
        echo "   Turbo boost: disabled"
    else
        echo "   Turbo boost: enabled"
    fi
fi
echo ""

echo "✅ Environment optimization complete!"
echo ""

echo "Next steps:"
echo "  1. Run tests with CPU pinning:"
echo "     taskset -c 0 cargo test --release -- --ignored manual_timing_run"
echo ""
echo "  2. For best results, close other applications and disable:" \
     "\n     - Web browsers" \
     "\n     - Background services" \
     "\n     - Network activity"
echo ""
echo "  3. To restore normal settings after testing:"
echo "     cpupower frequency-set --governor powersave"
echo "     echo 1 > /sys/devices/system/cpu/cpufreq/boost"
echo ""
