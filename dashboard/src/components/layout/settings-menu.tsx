"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Settings, Info, ExternalLink, LogOut } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"

export function SettingsMenu() {
  const router = useRouter()
  const [apiConfigOpen, setApiConfigOpen] = useState(false)
  const [aboutOpen, setAboutOpen] = useState(false)
  const [apiUrl, setApiUrl] = useState(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:6969')
  const [apiKey, setApiKey] = useState(process.env.API_KEY || '')

  const handleApiDocumentation = () => {
    window.open('http://localhost:6969/api/v1/docs', '_blank')
  }

  const handleGitHub = () => {
    window.open('https://github.com/madviking/headless-pm', '_blank')
  }

  const handleDisconnect = () => {
    // Clear local storage and redirect to login/setup
    localStorage.clear()
    router.push('/')
    router.refresh()
  }

  const handleSaveApiConfig = () => {
    // In a real app, you'd save these to a more persistent storage
    localStorage.setItem('apiUrl', apiUrl)
    localStorage.setItem('apiKey', apiKey)
    setApiConfigOpen(false)
    router.refresh()
  }

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon">
            <Settings className="h-[1.2rem] w-[1.2rem]" />
            <span className="sr-only">Settings</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>Settings</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onSelect={() => setApiConfigOpen(true)}>
            <Settings className="mr-2 h-4 w-4" />
            <span>API Configuration</span>
          </DropdownMenuItem>
          <DropdownMenuItem onSelect={() => setAboutOpen(true)}>
            <Info className="mr-2 h-4 w-4" />
            <span>About</span>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onSelect={handleApiDocumentation}>
            <ExternalLink className="mr-2 h-4 w-4" />
            <span>API Documentation</span>
          </DropdownMenuItem>
          <DropdownMenuItem onSelect={handleGitHub}>
            <ExternalLink className="mr-2 h-4 w-4" />
            <span>GitHub</span>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem className="text-destructive" onSelect={handleDisconnect}>
            <LogOut className="mr-2 h-4 w-4" />
            <span>Disconnect</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* API Configuration Dialog */}
      <Dialog open={apiConfigOpen} onOpenChange={setApiConfigOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>API Configuration</DialogTitle>
            <DialogDescription>
              Configure your Headless PM API connection settings.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="api-url">API URL</Label>
              <Input
                id="api-url"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="http://localhost:6969"
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="api-key">API Key</Label>
              <Input
                id="api-key"
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your API key"
              />
            </div>
          </div>
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setApiConfigOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveApiConfig}>
              Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* About Dialog */}
      <Dialog open={aboutOpen} onOpenChange={setAboutOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>About Headless PM</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Headless PM is a REST API for LLM agent task coordination with document-based communication.
            </p>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Version</span>
                <span className="font-medium">1.0.0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">API Version</span>
                <span className="font-medium">v1</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Dashboard</span>
                <span className="font-medium">Next.js 15.3.4</span>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}