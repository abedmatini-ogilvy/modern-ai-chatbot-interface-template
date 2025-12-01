"use client"

import React, { useEffect, useMemo, useRef, useState } from "react"
import { Calendar, LayoutGrid, MoreHorizontal } from "lucide-react"
import Sidebar from "./Sidebar"
import Header from "./Header"
import ChatPane from "./ChatPane"
import GhostIconButton from "./GhostIconButton"
import ThemeToggle from "./ThemeToggle"
import { INITIAL_CONVERSATIONS, INITIAL_FOLDERS } from "./mockData"
import { useResearchQuestions, useResearchSession } from "@/lib/use-research"
import { ResearchPhase } from "@/lib/api-client"

export default function AIAssistantUI() {
  const [theme, setTheme] = useState(() => {
    const saved = typeof window !== "undefined" && localStorage.getItem("theme")
    if (saved) return saved
    if (typeof window !== "undefined" && window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches)
      return "dark"
    return "light"
  })

  useEffect(() => {
    try {
      if (theme === "dark") document.documentElement.classList.add("dark")
      else document.documentElement.classList.remove("dark")
      document.documentElement.setAttribute("data-theme", theme)
      document.documentElement.style.colorScheme = theme
      localStorage.setItem("theme", theme)
    } catch {}
  }, [theme])

  useEffect(() => {
    try {
      const media = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)")
      if (!media) return
      const listener = (e) => {
        const saved = localStorage.getItem("theme")
        if (!saved) setTheme(e.matches ? "dark" : "light")
      }
      media.addEventListener("change", listener)
      return () => media.removeEventListener("change", listener)
    } catch {}
  }, [])

  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(() => {
    try {
      const raw = localStorage.getItem("sidebar-collapsed")
      return raw ? JSON.parse(raw) : { pinned: true, recent: false, folders: true, templates: true }
    } catch {
      return { pinned: true, recent: false, folders: true, templates: true }
    }
  })
  useEffect(() => {
    try {
      localStorage.setItem("sidebar-collapsed", JSON.stringify(collapsed))
    } catch {}
  }, [collapsed])

  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try {
      const saved = localStorage.getItem("sidebar-collapsed-state")
      return saved ? JSON.parse(saved) : false
    } catch {
      return false
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem("sidebar-collapsed-state", JSON.stringify(sidebarCollapsed))
    } catch {}
  }, [sidebarCollapsed])

  const [conversations, setConversations] = useState(INITIAL_CONVERSATIONS)
  const [selectedId, setSelectedId] = useState(null)
  const [folders, setFolders] = useState(INITIAL_FOLDERS)
  
  // Track which conversation is running research (using ref to avoid stale closure)
  const activeResearchConvIdRef = useRef(null)
  
  // Load research questions from API
  const { questions: apiQuestions, loading: questionsLoading } = useResearchQuestions()
  
  // Convert API questions to template format
  const templates = useMemo(() => {
    if (!apiQuestions || apiQuestions.length === 0) return []
    return apiQuestions.map(q => ({
      id: q.id,
      name: q.title,
      content: q.question,
      snippet: q.focus,
      search_terms: q.search_terms,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }))
  }, [apiQuestions])
  
  // Research session management
  const {
    sessionId: currentSessionId,
    status: researchStatus,
    result: researchResult,
    error: researchError,
    isRunning: isResearching,
    progressPercentage,
    currentAgent,
    start: startResearch,
    reset: resetResearch,
  } = useResearchSession({
    onProgress: (status) => {
      // Add progress updates as messages to the conversation that started the research
      const convId = activeResearchConvIdRef.current
      if (convId && status.progress_updates && status.progress_updates.length > 0) {
        const latestUpdate = status.progress_updates[status.progress_updates.length - 1]
        updateConversationWithProgress(convId, latestUpdate)
      }
    },
    onComplete: (result) => {
      // Add final result as message to the conversation that started the research
      const convId = activeResearchConvIdRef.current
      console.log('✅ Research onComplete called:', { convId, activeResearchConvIdRef, result })
      if (convId) {
        updateConversationWithResult(convId, result)
        // Switch to the conversation with results if not already viewing it
        setSelectedId(convId)
      }
      setIsThinking(false)
      setThinkingConvId(null)
      activeResearchConvIdRef.current = null
    },
    onError: (error) => {
      // Add error message to conversation that started the research
      const convId = activeResearchConvIdRef.current
      if (convId) {
        const errorMsg = {
          id: Math.random().toString(36).slice(2),
          role: "assistant",
          content: `❌ Research failed: ${error.message}`,
          createdAt: new Date().toISOString(),
          isError: true,
        }
        setConversations((prev) =>
          prev.map((c) => {
            if (c.id !== convId) return c
            const msgs = [...(c.messages || []), errorMsg]
            return { ...c, messages: msgs, updatedAt: new Date().toISOString() }
          })
        )
      }
      setIsThinking(false)
      setThinkingConvId(null)
      activeResearchConvIdRef.current = null
    },
  })
  
  const [query, setQuery] = useState("")
  const searchRef = useRef(null)

  const [isThinking, setIsThinking] = useState(false)
  const [thinkingConvId, setThinkingConvId] = useState(null)

  useEffect(() => {
    const onKey = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "n") {
        e.preventDefault()
        createNewChat()
      }
      if (!e.metaKey && !e.ctrlKey && e.key === "/") {
        const tag = document.activeElement?.tagName?.toLowerCase()
        if (tag !== "input" && tag !== "textarea") {
          e.preventDefault()
          searchRef.current?.focus()
        }
      }
      if (e.key === "Escape" && sidebarOpen) setSidebarOpen(false)
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [sidebarOpen, conversations])

  useEffect(() => {
    if (!selectedId && conversations.length > 0) {
      createNewChat()
    }
  }, [])

  const filtered = useMemo(() => {
    if (!query.trim()) return conversations
    const q = query.toLowerCase()
    return conversations.filter((c) => c.title.toLowerCase().includes(q) || c.preview.toLowerCase().includes(q))
  }, [conversations, query])

  const pinned = filtered.filter((c) => c.pinned).sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1))

  const recent = filtered
    .filter((c) => !c.pinned)
    .sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1))
    .slice(0, 10)

  const folderCounts = React.useMemo(() => {
    const map = Object.fromEntries(folders.map((f) => [f.name, 0]))
    for (const c of conversations) if (map[c.folder] != null) map[c.folder] += 1
    return map
  }, [conversations, folders])

  // Helper: Update conversation with progress message
  function updateConversationWithProgress(convId, progressUpdate) {
    const progressMsg = {
      id: `progress-${progressUpdate.timestamp}`,
      role: "assistant",
      content: progressUpdate.message,
      createdAt: progressUpdate.timestamp,
      isProgress: true,
      agent: progressUpdate.agent,
      status: progressUpdate.status,
    }
    
    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== convId) return c
        // Check if this progress message already exists
        const exists = (c.messages || []).some(m => m.id === progressMsg.id)
        if (exists) return c
        
        const msgs = [...(c.messages || []), progressMsg]
        return {
          ...c,
          messages: msgs,
          updatedAt: new Date().toISOString(),
          preview: progressMsg.content.slice(0, 80),
        }
      })
    )
  }
  
  // Helper: Update conversation with final result
  function updateConversationWithResult(convId, result) {
    console.log('📊 updateConversationWithResult called:', { convId, result })
    const now = new Date().toISOString()
    const messages = []
    
    // Safely extract data with defaults
    const socialMedia = result.data_collected?.social_media || {}
    const twitterCount = socialMedia.twitter?.total_results ?? 0
    const tiktokCount = socialMedia.tiktok?.total_results ?? 0
    const redditCount = socialMedia.reddit?.total_results ?? 0
    const webCount = result.data_collected?.web_intelligence?.total_results ?? 0
    const executionTime = result.execution_time_seconds?.toFixed(1) ?? '?'
    
    // Summary message
    const summaryMsg = {
      id: Math.random().toString(36).slice(2),
      role: "assistant",
      content: `✅ **Research Complete!**\n\nCollected **${result.total_data_points || 0}** data points in **${executionTime}s**\n\n- Twitter: ${twitterCount}\n- TikTok: ${tiktokCount}\n- Reddit: ${redditCount}\n- Web: ${webCount}`,
      createdAt: now,
      isResult: true,
    }
    messages.push(summaryMsg)
    console.log('📝 Created summary message:', summaryMsg)
    
    // Executive Summary
    if (result.executive_summary) {
      messages.push({
        id: Math.random().toString(36).slice(2),
        role: "assistant",
        content: `## Executive Summary\n\n${result.executive_summary}`,
        createdAt: now,
        isResult: true,
      })
    }
    
    // Key Findings
    if (result.key_findings && result.key_findings.length > 0) {
      messages.push({
        id: Math.random().toString(36).slice(2),
        role: "assistant",
        content: `## Key Findings\n\n${result.key_findings.map((f, i) => `${i + 1}. ${f}`).join('\n')}`,
        createdAt: now,
        isResult: true,
      })
    }
    
    // Recommendations
    if (result.recommendations && result.recommendations.length > 0) {
      messages.push({
        id: Math.random().toString(36).slice(2),
        role: "assistant",
        content: `## Recommendations\n\n${result.recommendations.map((r, i) => `${i + 1}. ${r}`).join('\n')}`,
        createdAt: now,
        isResult: true,
      })
    }
    
    // Full Report (if no structured data)
    if (!result.executive_summary && result.report) {
      messages.push({
        id: Math.random().toString(36).slice(2),
        role: "assistant",
        content: result.report,
        createdAt: now,
        isResult: true,
      })
    }
    
    setConversations((prev) => {
      console.log('📦 Updating conversations state, adding', messages.length, 'messages to conversation', convId)
      const updated = prev.map((c) => {
        if (c.id !== convId) return c
        const msgs = [...(c.messages || []), ...messages]
        console.log('✨ Updated conversation now has', msgs.length, 'messages')
        return {
          ...c,
          messages: msgs,
          updatedAt: now,
          messageCount: msgs.length,
          preview: messages[0].content.slice(0, 80),
        }
      })
      return updated
    })
  }

  function togglePin(id) {
    setConversations((prev) => prev.map((c) => (c.id === id ? { ...c, pinned: !c.pinned } : c)))
  }

  function createNewChat() {
    const id = Math.random().toString(36).slice(2)
    const item = {
      id,
      title: "New Chat",
      updatedAt: new Date().toISOString(),
      messageCount: 0,
      preview: "Say hello to start...",
      pinned: false,
      folder: "Work Projects",
      messages: [], // Ensure messages array is empty for new chats
    }
    setConversations((prev) => [item, ...prev])
    setSelectedId(id)
    setSidebarOpen(false)
  }

  function createFolder() {
    const name = prompt("Folder name")
    if (!name) return
    if (folders.some((f) => f.name.toLowerCase() === name.toLowerCase())) return alert("Folder already exists.")
    setFolders((prev) => [...prev, { id: Math.random().toString(36).slice(2), name }])
  }

  async function sendMessage(convId, content) {
    if (!content.trim()) return
    const now = new Date().toISOString()
    const userMsg = { id: Math.random().toString(36).slice(2), role: "user", content, createdAt: now }

    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== convId) return c
        const msgs = [...(c.messages || []), userMsg]
        return {
          ...c,
          messages: msgs,
          updatedAt: now,
          messageCount: msgs.length,
          preview: content.slice(0, 80),
        }
      }),
    )

    setIsThinking(true)
    setThinkingConvId(convId)

    // Check if this looks like a research question
    const isResearchQuestion = content.toLowerCase().includes('trend') || 
                              content.toLowerCase().includes('research') ||
                              content.includes('?')
    
    if (isResearchQuestion && apiQuestions && apiQuestions.length > 0) {
      // Start actual research
      setSelectedId(convId)
      try {
        await startResearch({
          question: content,
          search_query: content.split(/[?.!]/)[0].trim().slice(0, 100),
          conversation_id: convId,
        })
      } catch (error) {
        console.error('Research failed:', error)
        setIsThinking(false)
        setThinkingConvId(null)
      }
    } else {
      // Default mock response for non-research messages
      const currentConvId = convId
      setTimeout(() => {
        setIsThinking(false)
        setThinkingConvId(null)
        setConversations((prev) =>
          prev.map((c) => {
            if (c.id !== currentConvId) return c
            const ack = `Got it — I'll help with that.`
            const asstMsg = {
              id: Math.random().toString(36).slice(2),
              role: "assistant",
              content: ack,
              createdAt: new Date().toISOString(),
            }
            const msgs = [...(c.messages || []), asstMsg]
            return {
              ...c,
              messages: msgs,
              updatedAt: new Date().toISOString(),
              messageCount: msgs.length,
              preview: asstMsg.content.slice(0, 80),
            }
          }),
        )
      }, 1000)
    }
  }

  function editMessage(convId, messageId, newContent) {
    const now = new Date().toISOString()
    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== convId) return c
        const msgs = (c.messages || []).map((m) =>
          m.id === messageId ? { ...m, content: newContent, editedAt: now } : m,
        )
        return {
          ...c,
          messages: msgs,
          preview: msgs[msgs.length - 1]?.content?.slice(0, 80) || c.preview,
        }
      }),
    )
  }

  function resendMessage(convId, messageId) {
    const conv = conversations.find((c) => c.id === convId)
    const msg = conv?.messages?.find((m) => m.id === messageId)
    if (!msg) return
    sendMessage(convId, msg.content)
  }

  function pauseThinking() {
    setIsThinking(false)
    setThinkingConvId(null)
  }

  async function handleUseTemplate(template) {
    // Create a new conversation for this research
    const convId = Math.random().toString(36).slice(2)
    const now = new Date().toISOString()
    
    const newConv = {
      id: convId,
      title: template.name,
      updatedAt: now,
      messageCount: 0,
      preview: "Starting research...",
      pinned: false,
      folder: "Work Projects",
      messages: [
        {
          id: Math.random().toString(36).slice(2),
          role: "user",
          content: template.content,
          createdAt: now,
        },
        {
          id: Math.random().toString(36).slice(2),
          role: "assistant",
          content: "🔬 Starting research...",
          createdAt: now,
        },
      ],
    }
    
    setConversations((prev) => [newConv, ...prev])
    setSelectedId(convId)
    setSidebarOpen(false)
    
    // Start research
    setIsThinking(true)
    setThinkingConvId(convId)
    activeResearchConvIdRef.current = convId
    
    try {
      await startResearch({
        question_id: template.id,
        conversation_id: convId,
      })
    } catch (error) {
      console.error('Failed to start research:', error)
      setIsThinking(false)
      setThinkingConvId(null)
      activeResearchConvIdRef.current = null
    }
  }

  const composerRef = useRef(null)

  const selected = conversations.find((c) => c.id === selectedId) || null

  return (
    <div className="h-screen w-full bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      <div className="md:hidden sticky top-0 z-40 flex items-center gap-2 border-b border-zinc-200/60 bg-white/80 px-3 py-2 backdrop-blur dark:border-zinc-800 dark:bg-zinc-900/70">
        <div className="ml-1 flex items-center gap-2 text-sm font-semibold tracking-tight">
          <span className="inline-flex h-4 w-4 items-center justify-center">✱</span> AI Assistant
        </div>
        <div className="ml-auto flex items-center gap-2">
          <GhostIconButton label="Schedule">
            <Calendar className="h-4 w-4" />
          </GhostIconButton>
          <GhostIconButton label="Apps">
            <LayoutGrid className="h-4 w-4" />
          </GhostIconButton>
          <GhostIconButton label="More">
            <MoreHorizontal className="h-4 w-4" />
          </GhostIconButton>
          <ThemeToggle theme={theme} setTheme={setTheme} />
        </div>
      </div>

      <div className="mx-auto flex h-[calc(100vh-0px)] max-w-[1400px]">
        <Sidebar
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          theme={theme}
          setTheme={setTheme}
          collapsed={collapsed}
          setCollapsed={setCollapsed}
          sidebarCollapsed={sidebarCollapsed}
          setSidebarCollapsed={setSidebarCollapsed}
          conversations={conversations}
          pinned={pinned}
          recent={recent}
          folders={folders}
          folderCounts={folderCounts}
          selectedId={selectedId}
          onSelect={(id) => setSelectedId(id)}
          togglePin={togglePin}
          query={query}
          setQuery={setQuery}
          searchRef={searchRef}
          createFolder={createFolder}
          createNewChat={createNewChat}
          templates={templates}
          onUseTemplate={handleUseTemplate}
        />

        <main className="relative flex min-w-0 flex-1 flex-col">
          <Header createNewChat={createNewChat} sidebarCollapsed={sidebarCollapsed} setSidebarOpen={setSidebarOpen} />
          <ChatPane
            ref={composerRef}
            conversation={selected}
            onSend={(content) => selected && sendMessage(selected.id, content)}
            onEditMessage={(messageId, newContent) => selected && editMessage(selected.id, messageId, newContent)}
            onResendMessage={(messageId) => selected && resendMessage(selected.id, messageId)}
            isThinking={isThinking && thinkingConvId === selected?.id}
            onPauseThinking={pauseThinking}
          />
        </main>
      </div>
    </div>
  )
}
