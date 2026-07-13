<template>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="story in stories" :key="story.id" 
            class="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition cursor-pointer"
            @click="$emit('view', story)">
            <h3 class="font-semibold text-lg mb-2 line-clamp-1">{{story.title}}</h3>
            <p class="text-sm text-gray-500 mb-3">{{story.genre}} · {{story.style}} · {{story.word_count}}字</p>
            <p class="text-sm text-gray-600 line-clamp-3 mb-4">{{story.content}}</p>
            <div class="flex items-center justify-between">
                <span class="text-xs text-gray-400">{{formatDate(story.created_at)}}</span>
                <div class="flex gap-2">
                    <button @click.stop="$emit('continue', story)" class="text-purple-500 hover:text-purple-700" title="续写">
                        <i class="fa-solid fa-pen-nib"></i>
                    </button>
                    <button @click.stop="$emit('delete', story.id)" class="text-red-500 hover:text-red-700" title="删除">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>
        <div v-if="!stories || stories.length === 0" class="col-span-full text-center py-12 text-gray-400">
            <i class="fa-solid fa-inbox text-6xl mb-4"></i>
            <p>暂无历史记录</p>
        </div>
    </div>
</template>

<script>
export default {
    name: 'HistoryList',
    props: {
        stories: { type: Array, required: true }
    },
    emits: ['view', 'delete', 'continue'],
    methods: {
        formatDate(dateStr) {
            const date = new Date(dateStr)
            return date.toLocaleString('zh-CN')
        }
    }
}
</script>
