export function useStory() {
    const storyContent = ref('')
    const currentTitle = ref('')
    const isGenerating = ref(false)
    const history = ref([])
    const agents = reactive([
        { name: 'planner', label: '策划', status: 'waiting', message: '等待中', data: null, expanded: false },
        { name: 'character', label: '角色', status: 'waiting', message: '等待中', data: null, expanded: false },
        { name: 'writer', label: '写作', status: 'waiting', message: '等待中', data: null, expanded: false },
        { name: 'polisher', label: '润色', status: 'waiting', message: '等待中', data: null, expanded: false }
    ])

    const generateStory = async (formData, characters, foreshadowings) => {
        isGenerating.value = true
        storyContent.value = ''
        currentTitle.value = ''
        
        agents.forEach(agent => {
            agent.status = 'waiting'
            agent.message = '等待中'
            agent.data = null
        })

        const chars = characters.map(c => ({
            name: c.name,
            age: c.age,
            identity: c.identity,
            appearance: c.appearance,
            personality: c.personality,
            background: c.background,
            motivation: c.motivation,
            tags: c.tags,
            relationships: c.relationships
        }))

        try {
            const response = await fetch('/api/story/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    theme: formData.theme,
                    genre: formData.genre,
                    style: formData.style,
                    length: formData.length,
                    background: formData.background,
                    perspective: formData.perspective,
                    conflict: formData.conflict,
                    mood: formData.mood,
                    outline: formData.outline,
                    characters: chars,
                    api_key: apiKey.value,
                    world_setting: formData.world_setting,
                    foreshadowings: foreshadowings,
                    continuation_mode: formData.continuation_mode,
                    previous_story_id: formData.previous_story_id
                })
            })

            if (!response.ok) {
                throw new Error('Network response was not ok')
            }

            const reader = response.body.getReader()
            const decoder = new TextDecoder()

            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                const chunk = decoder.decode(value)
                const lines = chunk.split('\n')

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.substring(6))
                            
                            if (data.agent && data.status) {
                                const agent = agents.find(a => a.name === data.agent)
                                if (agent) {
                                    agent.status = data.status
                                    agent.message = data.message || ''
                                }
                                
                                if (data.data) {
                                    if (agent) {
                                        agent.data = data.data
                                    }
                                    if (data.agent === 'writer' && data.status === 'writing') {
                                        storyContent.value += data.data
                                    } else if (data.agent === 'polisher' && data.status === 'writing') {
                                        storyContent.value = data.data
                                    } else if (data.agent === 'writer' && data.status === 'done') {
                                        storyContent.value = data.data.content || data.data
                                    }
                                }

                                if (data.agent === 'orchestrator' && data.status === 'complete') {
                                    currentTitle.value = data.data.title || formData.theme
                                    storyContent.value = data.data.content || storyContent.value
                                }
                            }
                        } catch (e) {
                            console.error('Parse error:', e)
                        }
                    }
                }
            }
        } catch (e) {
            console.error('Generation error:', e)
        } finally {
            isGenerating.value = false
            if (storyContent.value.trim()) {
                await saveStory(false)
            }
        }
    }

    const saveStory = async (showAlert = true) => {
        try {
            const response = await fetch('/api/story/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: currentTitle.value || storyForm.theme,
                    content: storyContent.value,
                    theme: storyForm.theme,
                    genre: storyForm.genre,
                    style: storyForm.style,
                    world_setting: storyForm.world_setting,
                    foreshadowings: foreshadowings.value,
                    previous_story_id: storyForm.previous_story_id
                })
            })
            await response.json()
            await loadHistory()
            if (showAlert) alert('保存成功')
        } catch (e) {
            console.error(e)
        }
    }

    const copyStory = () => {
        navigator.clipboard.writeText(storyContent.value)
        alert('已复制到剪贴板')
    }

    const loadHistory = async () => {
        try {
            const response = await fetch('/api/history')
            const data = await response.json()
            history.value = data?.stories || []
        } catch (e) {
            console.error(e)
        }
    }

    const viewStory = (story) => {
        selectedStory.value = story
        currentTab.value = 'history'
    }

    const deleteStory = async (storyId) => {
        if (!confirm('确定要删除这个故事吗？')) return
        try {
            const response = await fetch(`/api/history/${storyId}`, { method: 'DELETE' })
            await response.json()
            await loadHistory()
        } catch (e) {
            console.error(e)
        }
    }

    const continueStory = (story) => {
        storyForm.previous_story_id = story.id
        storyForm.theme = story.theme + ' - 续写'
        storyForm.world_setting = story.world_setting || ''
        foreshadowings.value = story.foreshadowings || []
        currentTab.value = 'create'
        alert('已加载前作信息，您可以继续创作后续章节！')
    }

    return {
        storyContent,
        currentTitle,
        isGenerating,
        history,
        agents,
        generateStory,
        saveStory,
        copyStory,
        loadHistory,
        viewStory,
        deleteStory,
        continueStory
    }
}
