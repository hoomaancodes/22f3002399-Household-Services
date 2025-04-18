<template>
  <div class="card service-card h-100" @click="handleClick">
    <div v-if="imageUrl" class="service-image-container">
      <img :src="imageUrl" class="card-img-top" :alt="service.name">
    </div>
    <div class="card-body">
      <h5 class="card-title">{{ service.name }}</h5>
      <p class="card-text">{{ service.description || 'No description available' }}</p>
      <div class="service-details">
        <div class="service-price">
          <strong>₹{{ service.price }}</strong>
        </div>
        <div class="service-time">
          <i class="far fa-clock"></i> {{ service.time_req }} mins
        </div>
      </div>
      <div class="service-type mt-2">
        <span class="badge badge-primary">{{ service.service_type }}</span>
      </div>
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ServiceCard',
  props: {
    service: {
      type: Object,
      required: true
    },
    imageUrl: {
      type: String,
      default: null
    },
    clickable: {
      type: Boolean,
      default: true
    }
  },
  methods: {
    handleClick() {
      if (this.clickable) {
        this.$emit('click', this.service);
      }
    }
  }
};
</script>

<style scoped>
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  margin-bottom: 1rem;
}
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.service-details {
  margin-top: 1rem;
  margin-bottom: 1rem;
}
.card-body {
  display: flex;
  flex-direction: column;
  height: 100%;
}
</style> 