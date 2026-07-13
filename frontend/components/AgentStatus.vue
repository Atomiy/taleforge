<template>
    <div class="bg-white rounded-2xl shadow-lg p-6">
        <h2 class="text-lg font-semibold mb-4 flex items-center">
            <i class="fa-solid fa-robot text-blue-500 mr-2"></i>创作进度
        </h2>
        <div class="space-y-3">
            <div v-for="agent in agents" :key="agent.name" 
                :class="['border-2 rounded-xl p-4 transition', getAgentClass(agent)]">
                <div class="flex items-center justify-between cursor-pointer" @click="agent.expanded = !agent.expanded">
                    <div class="flex items-center gap-3">
                        <i :class="['fa-solid text-xl', getAgentIcon(agent)]"></i>
                        <div>
                            <h3 class="font-medium">{{agent.label}}</h3>
                            <p class="text-sm text-gray-500">{{agent.message}}</p>
                        </div>
                    </div>
                    <i :class="['fa-solid transition-transform', agent.expanded ? 'fa-chevron-down rotate-180' : 'fa-chevron-down']"></i>
                </div>
                <div v-if="agent.expanded && agent.data" class="mt-4 p-3 bg-gray-50 rounded-lg">
                    <pre class="text-sm text-gray-700 overflow-x-auto">{{JSON.stringify(agent.data, null, 2)}}</pre>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AgentStatus',
    props: {
        agents: { type: Array, required: true }
    },
    methods: {
        getAgentClass(agent) {
            switch(agent.status) {
                case 'running': return 'border-yellow-400 bg-yellow-50';
                case 'writing': return 'border-blue-400 bg-blue-50';
                case 'done': return 'border-green-400';
                case 'error': return 'border-red-400 bg-red-50';
                default: return 'border-gray-200 bg-gray-50';
            }
        },
        getAgentIcon(agent) {
            const icons = {
                planner: 'fa-lightbulb text-yellow-500',
                character: 'fa-user text-pink-500',
                writer: 'fa-pen-fancy text-blue-500',
                polisher: 'fa-spell-check text-green-500',
                image: 'fa-image text-purple-500'
            }
            return icons[agent.name] || 'fa-robot text-gray-500'
        }
    }
}
</script>
