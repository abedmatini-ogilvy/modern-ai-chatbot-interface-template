"use client"

import { useState, useRef, useEffect } from "react"
import { FileText, MoreHorizontal, Copy, Edit3, Trash2 } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

export default function TemplateRow({ template, onUseTemplate, onEditTemplate, onRenameTemplate, onDeleteTemplate }) {
  const [showMenu, setShowMenu] = useState(false)
  const menuRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false)
      }
    }

    if (showMenu) {
      document.addEventListener("mousedown", handleClickOutside)
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [showMenu])

  const handleUse = () => {
    onUseTemplate?.(template)
    setShowMenu(false)
  }

  const handleEdit = () => {
    onEditTemplate?.(template)
    setShowMenu(false)
  }

  const handleRename = () => {
    const newName = prompt(`Rename template "${template.name}" to:`, template.name)
    if (newName && newName.trim() && newName !== template.name) {
      onRenameTemplate?.(template.id, newName.trim())
    }
    setShowMenu(false)
  }

  const handleDelete = () => {
    if (confirm(`Are you sure you want to delete the template "${template.name}"?`)) {
      onDeleteTemplate?.(template.id)
    }
    setShowMenu(false)
  }

  return (
    <div className="group">
      <div className="flex items-center justify-between rounded-lg px-2 py-2 text-sm hover:bg-zinc-100 dark:hover:bg-zinc-800">
        <button
          onClick={handleUse}
          className="flex items-center gap-2 flex-1 text-left min-w-0"
          title={`Use template: ${template.snippet}`}
        >
          <FileText className="h-4 w-4 text-zinc-500 shrink-0" />
          <div className="min-w-0 flex-1">
            <div className="truncate font-medium">{template.name}</div>
            <div className="truncate text-xs text-zinc-500 dark:text-zinc-400">{template.snippet}</div>
          </div>
        </button>

        <div className="flex items-center gap-1">
          <span className="hidden group-hover:inline text-xs text-zinc-500 dark:text-zinc-400 px-1">Click to start research</span>
        </div>
      </div>
    </div>
  )
}
