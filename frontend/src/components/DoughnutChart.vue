<template>
  <div style="position: relative; width: 100%; height: 250px;">
    <Doughnut :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps({
  labels: {
    type: Array,
    required: true
  },
  data: {
    type: Array,
    required: true
  }
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
  return {
    labels: props.labels,
    datasets: [
      {
        backgroundColor: backgroundColors.slice(0, props.data.length),
        borderColor: '#1A233A', // Match card background to create a gap effect
        borderWidth: 2,
        data: props.data
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '75%', // Make the doughnut thin and modern
  plugins: {
    legend: {
      position: 'right',
      labels: {
        color: '#F8FAFC',
        font: {
          family: "'Inter', sans-serif",
          size: 12
        },
        usePointStyle: true,
        padding: 20
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
            label += new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(context.parsed);
          }
          return label;
        }
      }
    }
  }
}
</script>
