import React, { useEffect, useState, useRef } from "react";
import {
  CheckCircle2,
  Cpu,
  Fingerprint,
  KeyRound,
  Lock,
  Moon,
  Scan,
  Sun,
  Volume2,
  VolumeX,
  Zap,
} from "lucide-react";
import { BrandLogo } from "@/components/common/BrandLogo";
import { cyberAudio } from "@/utils/cyberAudio";
import { useTheme } from "@/hooks/useTheme";

export interface LoginPageProps {
  onLoginSuccess: (agentInfo: { id: string; name: string; role: string; clearance: string }) => void;
  onNavigateOverviewDirect?: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({
  onLoginSuccess,
  onNavigateOverviewDirect,
}) => {
  const { theme, toggleTheme } = useTheme();

  // Credentials state
  const [authMode, setAuthMode] = useState<"credentials" | "biometric">("credentials");
  const [agentId, setAgentId] = useState("AGENT-CYBER-941");
  const [selectedRole, setSelectedRole] = useState("Lead Specialist");
  const [passphrase, setPassphrase] = useState("••••••••••••••••");
  const [showPassphrase, setShowPassphrase] = useState(false);
  const [isSoundMuted, setIsSoundMuted] = useState(false);

  // Animation states
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationStage, setVerificationStage] = useState<number>(0);
  const [isAccessGranted, setIsAccessGranted] = useState(false);
  const [isBiometricScanning, setIsBiometricScanning] = useState(false);
  const [biometricProgress, setBiometricProgress] = useState(0);

  // Live clock
  const [currentTime, setCurrentTime] = useState("");

  const biometricIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Live Clock (concise UTC)
  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      const pad = (n: number) => n.toString().padStart(2, "0");
      setCurrentTime(
        `${pad(now.getUTCHours())}:${pad(now.getUTCMinutes())}:${pad(now.getUTCSeconds())} UTC`
      );
    };
    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, []);

  const toggleAudio = () => {
    const muted = cyberAudio.toggleMute();
    setIsSoundMuted(muted);
  };

  const handleSelectPreset = (id: string, role: string) => {
    cyberAudio.playKeyClick();
    setAgentId(id);
    setSelectedRole(role);
    setPassphrase("EnclaveKey-941");
  };

  // Gamified, brisk cyber-access sequence
  const startAuthenticationSequence = (role: string = selectedRole) => {
    if (isVerifying) return;

    cyberAudio.playScanChirp();
    setIsVerifying(true);
    setVerificationStage(1);

    setTimeout(() => {
      cyberAudio.playGlitchPulse();
      setVerificationStage(2);
    }, 450);

    setTimeout(() => {
      cyberAudio.playScanChirp();
      setVerificationStage(3);
    }, 900);

    setTimeout(() => {
      cyberAudio.playAccessGranted();
      setVerificationStage(4);
      setIsAccessGranted(true);

      setTimeout(() => {
        onLoginSuccess({
          id: agentId || "AGENT-941",
          name: "Agent Lead",
          role: role,
          clearance: "LEVEL-4 ACCESS",
        });
      }, 700);
    }, 1350);
  };

  // Biometric interaction
  const handleBiometricClick = () => {
    if (isVerifying || isAccessGranted) return;
    cyberAudio.playScanChirp();
    setIsBiometricScanning(true);
    setBiometricProgress(0);

    let prog = 0;
    biometricIntervalRef.current = setInterval(() => {
      prog += 20;
      setBiometricProgress(prog);
      if (prog >= 100) {
        if (biometricIntervalRef.current) clearInterval(biometricIntervalRef.current);
        setIsBiometricScanning(false);
        startAuthenticationSequence("Biometric Agent");
      }
    }, 80);
  };

  return (
    <div className="relative min-h-screen w-full bg-bg-primary text-text-primary flex flex-col justify-between overflow-hidden select-none font-sans transition-colors duration-250">
      {/* Dynamic Cyber Radar & Ambient Glow */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_35%,rgba(14,40,78,0.35)_0%,transparent_70%)] dark:bg-[radial-gradient(circle_at_50%_35%,rgba(14,40,78,0.6)_0%,rgba(3,7,18,0.98)_70%)]" />
        <div className="absolute inset-0 cyber-grid opacity-25 dark:opacity-35" />

        {/* Rotating Radar Sweep */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full border border-accent-blue/15 pointer-events-none">
          <div className="absolute inset-0 rounded-full border border-accent-cyan/10 scale-75" />
          <div className="absolute inset-0 rounded-full border border-accent-cyan/10 scale-50" />
          <div className="absolute inset-0 rounded-full animate-radar origin-center bg-[conic-gradient(from_0deg,transparent_0deg,transparent_270deg,rgba(34,211,238,0.06)_330deg,rgba(34,211,238,0.22)_360deg)]" />
        </div>
      </div>

      {/* Clean Top Bar with Audio & Theme Switcher */}
      <header className="relative z-20 px-6 py-4 flex items-center justify-between text-xs font-mono">
        <div className="flex items-center gap-2 text-text-muted">
          <span className="w-2 h-2 rounded-full bg-status-success animate-pulse" />
          <span className="font-semibold text-text-primary">SYSTEM ONLINE</span>
          <span className="hidden sm:inline text-border-default">•</span>
          <span className="hidden sm:inline text-text-muted">{currentTime}</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Theme Mode Toggle */}
          <button
            onClick={toggleTheme}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-primary border border-border-default hover:border-accent-cyan text-text-muted hover:text-text-primary transition-colors shadow-sm"
            title={`Switch to ${theme === "dark" ? "Light" : "Dark"} mode`}
          >
            {theme === "dark" ? (
              <Sun className="w-3.5 h-3.5 text-amber-400" />
            ) : (
              <Moon className="w-3.5 h-3.5 text-accent-indigo" />
            )}
            <span className="hidden sm:inline">{theme === "dark" ? "LIGHT THEME" : "DARK THEME"}</span>
          </button>

          {/* Sound FX Toggle */}
          <button
            onClick={toggleAudio}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-primary border border-border-default hover:border-accent-cyan text-text-muted hover:text-accent-cyan transition-colors shadow-sm"
            title="Toggle Cyber Sound Effects"
          >
            {isSoundMuted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5 text-accent-cyan" />}
            <span className="hidden sm:inline">{isSoundMuted ? "MUTE" : "SOUND ON"}</span>
          </button>
        </div>
      </header>

      {/* Centerpiece Login Terminal Card */}
      <main className="relative z-20 flex-1 flex items-center justify-center p-4 sm:p-6 my-auto">
        <div className="relative w-full max-w-md">
          {/* Subtle Cyber Corner Brackets */}
          <div className="absolute -top-2 -left-2 w-4 h-4 border-t-2 border-l-2 border-accent-cyan/80 pointer-events-none" />
          <div className="absolute -top-2 -right-2 w-4 h-4 border-t-2 border-r-2 border-accent-cyan/80 pointer-events-none" />
          <div className="absolute -bottom-2 -left-2 w-4 h-4 border-b-2 border-l-2 border-accent-cyan/80 pointer-events-none" />
          <div className="absolute -bottom-2 -right-2 w-4 h-4 border-b-2 border-r-2 border-accent-cyan/80 pointer-events-none" />

          {/* Clean Glassmorphic Card — Adaptive to Both Themes */}
          <div className="relative rounded-2xl bg-surface-primary border border-border-default shadow-card p-6 sm:p-8 overflow-hidden transition-colors duration-250">
            {/* Ambient Scanline */}
            <div className="absolute inset-x-0 h-[1.5px] bg-gradient-to-r from-transparent via-accent-cyan/70 to-transparent animate-scanline pointer-events-none" />

            {/* Official Brand Logo (Pure Vector SVG, No Square Box/Border, Single-Line Tagline) */}
            <div className="flex flex-col items-center text-center mb-6">
              <BrandLogo
                size="xl"
                layout="stacked"
                showText={true}
                showTagline={true}
                interactive={false}
              />
            </div>

            {/* Verification In-Progress View */}
            {isVerifying ? (
              <div className="py-6 space-y-5 animate-fade-in text-center font-mono">
                <div className="p-4 rounded-xl bg-surface-secondary border border-border-default shadow-sm">
                  <Cpu className="w-8 h-8 mx-auto mb-3 animate-spin text-accent-cyan" />
                  <p className="text-xs font-bold text-accent-cyan uppercase tracking-wider">
                    {verificationStage === 1
                      ? "Verifying Credentials..."
                      : verificationStage === 2
                      ? "Checking Enclave Security..."
                      : verificationStage === 3
                      ? "Loading Investigation Workspace..."
                      : "Access Confirmed!"}
                  </p>

                  {/* Progress bar */}
                  <div className="h-2 w-full bg-surface-primary rounded-full overflow-hidden p-0.5 border border-border-default mt-4">
                    <div
                      className={`h-full rounded-full transition-all duration-300 ${
                        isAccessGranted
                          ? "bg-status-success shadow-[0_0_15px_rgba(16,185,129,0.8)]"
                          : "bg-gradient-to-r from-accent-blue to-accent-cyan shadow-[0_0_10px_rgba(34,211,238,0.7)]"
                      }`}
                      style={{
                        width:
                          verificationStage === 1
                            ? "33%"
                            : verificationStage === 2
                            ? "66%"
                            : "100%",
                      }}
                    />
                  </div>
                </div>

                {isAccessGranted && (
                  <div className="p-3.5 rounded-xl bg-status-success/15 border border-status-success text-status-success font-bold text-sm tracking-wider uppercase animate-fade-in flex items-center justify-center gap-2">
                    <CheckCircle2 className="w-5 h-5" />
                    <span>ACCESS GRANTED • WELCOME</span>
                  </div>
                )}
              </div>
            ) : (
              /* Simple, Intuitive Login Form */
              <div className="space-y-5">
                {/* Clean Tab Switcher */}
                <div className="grid grid-cols-2 gap-1.5 p-1 rounded-xl bg-surface-secondary border border-border-default font-mono text-xs">
                  <button
                    onClick={() => {
                      cyberAudio.playKeyClick();
                      setAuthMode("credentials");
                    }}
                    className={`py-2 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${
                      authMode === "credentials"
                        ? "bg-accent-blue/15 text-accent-cyan border border-accent-blue/30 shadow-sm font-bold"
                        : "text-text-muted hover:text-text-primary"
                    }`}
                  >
                    <KeyRound className="w-3.5 h-3.5" />
                    <span>PASSWORD</span>
                  </button>

                  <button
                    onClick={() => {
                      cyberAudio.playKeyClick();
                      setAuthMode("biometric");
                    }}
                    className={`py-2 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all ${
                      authMode === "biometric"
                        ? "bg-accent-blue/15 text-accent-cyan border border-accent-blue/30 shadow-sm font-bold"
                        : "text-text-muted hover:text-text-primary"
                    }`}
                  >
                    <Fingerprint className="w-3.5 h-3.5" />
                    <span>FINGERPRINT</span>
                  </button>
                </div>

                {authMode === "credentials" ? (
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      startAuthenticationSequence();
                    }}
                    className="space-y-4"
                  >
                    <div>
                      <label className="block text-xs font-mono text-text-secondary mb-1">
                        AGENT ID
                      </label>
                      <input
                        type="text"
                        value={agentId}
                        onChange={(e) => setAgentId(e.target.value)}
                        placeholder="e.g. AGENT-941"
                        required
                        className="w-full px-3.5 py-2.5 rounded-xl bg-surface-secondary border border-border-default text-text-primary font-mono text-xs focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan outline-none transition-all"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-mono text-text-secondary mb-1 flex justify-between">
                        <span>PASSWORD</span>
                        <button
                          type="button"
                          onClick={() => setShowPassphrase(!showPassphrase)}
                          className="text-[10px] text-accent-cyan hover:underline"
                        >
                          {showPassphrase ? "Hide" : "Show"}
                        </button>
                      </label>
                      <input
                        type={showPassphrase ? "text" : "password"}
                        value={passphrase}
                        onChange={(e) => setPassphrase(e.target.value)}
                        placeholder="Enter password"
                        required
                        className="w-full px-3.5 py-2.5 rounded-xl bg-surface-secondary border border-border-default text-text-primary font-mono text-xs focus:border-accent-cyan focus:ring-1 focus:ring-accent-cyan outline-none transition-all"
                      />
                    </div>

                    {/* Quick Preset Roles */}
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono text-text-muted uppercase">Roles:</span>
                      <button
                        type="button"
                        onClick={() => handleSelectPreset("AGENT-CYBER-941", "Lead Specialist")}
                        className="px-2 py-1 rounded bg-surface-secondary hover:bg-surface-hover border border-border-default text-[10px] font-mono text-text-secondary hover:text-accent-cyan transition-colors"
                      >
                        Lead Analyst
                      </button>
                      <button
                        type="button"
                        onClick={() => handleSelectPreset("IR-RESP-042", "Incident Responder")}
                        className="px-2 py-1 rounded bg-surface-secondary hover:bg-surface-hover border border-border-default text-[10px] font-mono text-text-secondary hover:text-accent-cyan transition-colors"
                      >
                        Responder
                      </button>
                      <button
                        type="button"
                        onClick={() => handleSelectPreset("AUDIT-EXT-107", "Auditor")}
                        className="px-2 py-1 rounded bg-surface-secondary hover:bg-surface-hover border border-border-default text-[10px] font-mono text-text-secondary hover:text-accent-cyan transition-colors"
                      >
                        Auditor
                      </button>
                    </div>

                    {/* Big Action Button */}
                    <button
                      type="submit"
                      className="w-full py-3 rounded-xl bg-gradient-to-r from-accent-blue via-accent-cyan to-accent-blue text-slate-950 font-black font-mono text-xs uppercase tracking-wider shadow-glow-cyan hover:shadow-[0_0_25px_rgba(34,211,238,0.7)] hover:scale-[1.01] active:scale-[0.99] transition-all flex items-center justify-center gap-2 mt-2"
                    >
                      <Lock className="w-4 h-4 text-slate-950" />
                      <span>SIGN IN</span>
                    </button>
                  </form>
                ) : (
                  /* Biometric Scanner */
                  <div className="py-2 text-center space-y-4">
                    <p className="text-xs text-text-secondary font-mono">
                      Click sensor to scan fingerprint
                    </p>

                    <div className="flex justify-center">
                      <div
                        onClick={handleBiometricClick}
                        className={`relative w-28 h-28 rounded-2xl cursor-pointer flex flex-col items-center justify-center border-2 transition-all duration-300 ${
                          isBiometricScanning
                            ? "border-accent-cyan bg-accent-cyan/10 shadow-[0_0_30px_rgba(34,211,238,0.6)] scale-105"
                            : "border-accent-blue/30 bg-surface-secondary hover:border-accent-cyan hover:shadow-glow-cyan"
                        }`}
                      >
                        {isBiometricScanning && (
                          <div className="absolute inset-x-0 h-1 bg-gradient-to-r from-transparent via-accent-cyan to-transparent animate-scanline pointer-events-none" />
                        )}

                        <Fingerprint
                          className={`w-14 h-14 transition-colors ${
                            isBiometricScanning ? "text-accent-cyan animate-pulse" : "text-text-muted"
                          }`}
                        />

                        <span className="text-[10px] font-mono font-bold text-accent-cyan mt-1">
                          {isBiometricScanning ? `${biometricProgress}%` : "TAP TO SCAN"}
                        </span>

                        <Scan className="absolute inset-2 w-full h-full text-accent-blue/15 pointer-events-none" />
                      </div>
                    </div>
                  </div>
                )}

                {/* 1-Click Instant Guest Login */}
                <div className="pt-2 border-t border-border-default flex items-center justify-between text-[11px] font-mono text-text-muted">
                  <span>Fast Demo Mode</span>
                  <button
                    type="button"
                    onClick={() => {
                      if (onNavigateOverviewDirect) {
                        onNavigateOverviewDirect();
                      } else {
                        startAuthenticationSequence("Guest Analyst");
                      }
                    }}
                    className="text-accent-cyan hover:underline flex items-center gap-1 font-bold"
                  >
                    <span>Instant Login</span>
                    <Zap className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Clean Footer */}
      <footer className="relative z-20 px-6 py-3 text-center text-xs font-mono text-text-muted">
        ForensiWeb • Digital Forensics &amp; Security Platform
      </footer>
    </div>
  );
};
