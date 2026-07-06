<template>
  <div style="position: relative; width: 100%; height: 250px;">
    <Pie :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Pie } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  labels: {
    type: Array,
    required: true
  },
  data: {
    type: Array,
    required: true
  },
  colors: {
    type: Array,
    required: false
  }
})

const isMobile = ref(false)
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

// Use a vibrant color palette that matches the dark glassmorphism theme
const backgroundColors = [
  '#3B82F6', // Blue
  '#8B5CF6', // Purple
  '#10B981', // Green
  '#F59E0B', // Yellow
  '#EF4444', // Red
  '#06B6D4', // Cyan
  '#EC4899', // Pink
  '#6366F1'  // Indigo
]

const chartData = computed(() => {
  const bgColors = props.colors || backgroundColors.slice(0, props.data.length);
  return {
    labels: props.labels,
    datasets: [
      {
        backgroundColor: bgColors,
        borderColor: '#080b11', // Match obsidian body background for premium gap cutout effect
        borderWidth: 2,
        data: props.data
      }
    ]
  }
})

const chartOptions = computed(() => {
  const total = props.data.reduce((a, b) => Number(a) + Number(b), 0)
  const formattedTotal = 'RM' + new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(total)

  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: isMobile.value ? 'bottom' : 'right',
        title: {
          display: true,
          text: `Total: ${formattedTotal}`,
          color: '#F8FAFC',
          font: {
            family: "'Inter', sans-serif",
            size: 14,
            weight: 'bold'
          },
          padding: { bottom: 15 }
        },
        labels: {
          color: '#F8FAFC',
          font: {
            family: "'Inter', sans-serif",
            size: 12
          },
          usePointStyle: true,
          padding: 20,
          generateLabels: function(chart) {
            const data = chart.data;
            if (data.labels.length && data.datasets.length) {
              const dataset = data.datasets[0];
              const totalVal = dataset.data.reduce((a, b) => Number(a) + Number(b), 0);
              return data.labels.map((label, i) => {
                const val = dataset.data[i];
                const percentage = totalVal > 0 ? Math.round((val / totalVal) * 100) : 0;
                const meta = chart.getDatasetMeta(0);
                const style = meta.controller.getStyle(i);

                return {
                  text: `${label} (${percentage}%)`,
                  fillStyle: style.backgroundColor,
                  strokeStyle: style.borderColor,
                  lineWidth: style.borderWidth,
                  hidden: isNaN(dataset.data[i]) || meta.data[i].hidden,
                  index: i
                };
              });
            }
            return [];
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(19, 27, 47, 0.9)',
        titleColor: '#F8FAFC',
        bodyColor: '#F8FAFC',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            let label = context.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed !== null) {
              const val = context.parsed;
              const totalVal = context.dataset.data.reduce((a, b) => Number(a) + Number(b), 0);
              const percentage = totalVal > 0 ? Math.round((val / totalVal) * 100) : 0;
              label += 'RM' + new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val);
              label += ` (${percentage}%)`;
            }
            return label;
          }
        }
      }
    }
  }
})
</script>
