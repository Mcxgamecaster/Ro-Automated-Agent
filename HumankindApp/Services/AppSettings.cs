using System;

namespace HumankindApp.Services;

public sealed class AppSettings
{
    public string ConfigPath { get; set; } = "configs/humankind3.yaml";
    public string Profile { get; set; } = "windowed";
    public string PythonExecutable { get; set; } = "python";

    public string Planner { get; set; } = "rules";
    public string GeminiModel { get; set; } = "gemini-2.5-flash";
    public double GeminiIntervalSeconds { get; set; } = 1.5;
    public bool GeminiSendVision { get; set; } = true;

    public bool AssistMode { get; set; } = true;
    public bool DebugMode { get; set; } = false;
    public int? FpsOverride { get; set; } = null;
    public bool DryRun { get; set; } = false;

    public string? EncryptedGeminiApiKey { get; set; } = null;
}
