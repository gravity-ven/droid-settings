#!/usr/bin/env node
/**
 * MCP Server for Computer Use via MANUS
 * Exposes computer use capabilities through MCP protocol
 */

const { spawn } = require('child_process');
const readline = require('readline');
const os = require('os');
const path = require('path');

class ComputerUseMCPServer {
  constructor() {
    this.agentsDir = path.join(os.homedir(), '.claude', 'agents');
  }

  async initialize() {
    this.sendResponse({
      jsonrpc: '2.0',
      id: null,
      result: {
        protocolVersion: '2024-11-05',
        serverInfo: {
          name: 'computer-use',
          version: '1.0.0'
        },
        capabilities: {
          tools: {}
        }
      }
    });
  }

  async listTools() {
    return {
      tools: [
        {
          name: 'run_computer_task',
          description: 'Execute a computer use task with autonomous browser automation',
          inputSchema: {
            type: 'object',
            properties: {
              task: {
                type: 'string',
                description: 'Natural language task description (e.g., "Navigate to example.com and take screenshot")'
              },
              max_steps: {
                type: 'number',
                description: 'Maximum execution steps (default: 50)',
                default: 50
              }
            },
            required: ['task']
          }
        },
        {
          name: 'computer_screenshot',
          description: 'Take a screenshot of the current browser window',
          inputSchema: {
            type: 'object',
            properties: {
              full_page: {
                type: 'boolean',
                description: 'Capture full page or viewport only',
                default: true
              },
              output_path: {
                type: 'string',
                description: 'Path to save screenshot (optional)'
              }
            }
          }
        },
        {
          name: 'computer_click',
          description: 'Click at pixel coordinates',
          inputSchema: {
            type: 'object',
            properties: {
              x: {
                type: 'number',
                description: 'X coordinate in pixels'
              },
              y: {
                type: 'number',
                description: 'Y coordinate in pixels'
              }
            },
            required: ['x', 'y']
          }
        },
        {
          name: 'computer_type',
          description: 'Type text into the current element',
          inputSchema: {
            type: 'object',
            properties: {
              text: {
                type: 'string',
                description: 'Text to type'
              }
            },
            required: ['text']
          }
        },
        {
          name: 'computer_key',
          description: 'Press a keyboard key',
          inputSchema: {
            type: 'object',
            properties: {
              key: {
                type: 'string',
                description: 'Key to press (Enter, Escape, Tab, etc.)'
              }
            },
            required: ['key']
          }
        }
      ]
    };
  }

  async executeTool(name, args) {
    const pythonScript = path.join(this.agentsDir, 'mcp_executor.py');

    return new Promise((resolve, reject) => {
      const proc = spawn('python3', [pythonScript, name, JSON.stringify(args)]);

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      proc.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      proc.on('close', (code) => {
        if (code === 0) {
          try {
            const result = JSON.parse(stdout);
            resolve({
              content: [
                {
                  type: 'text',
                  text: JSON.stringify(result, null, 2)
                }
              ]
            });
          } catch (e) {
            resolve({
              content: [
                {
                  type: 'text',
                  text: stdout
                }
              ]
            });
          }
        } else {
          reject(new Error(`Execution failed: ${stderr}`));
        }
      });
    });
  }

  sendResponse(response) {
    console.log(JSON.stringify(response));
  }

  async handleRequest(request) {
    try {
      if (request.method === 'initialize') {
        await this.initialize();
      } else if (request.method === 'tools/list') {
        const tools = await this.listTools();
        this.sendResponse({
          jsonrpc: '2.0',
          id: request.id,
          result: tools
        });
      } else if (request.method === 'tools/call') {
        const result = await this.executeTool(request.params.name, request.params.arguments);
        this.sendResponse({
          jsonrpc: '2.0',
          id: request.id,
          result: result
        });
      } else {
        this.sendResponse({
          jsonrpc: '2.0',
          id: request.id,
          error: {
            code: -32601,
            message: 'Method not found'
          }
        });
      }
    } catch (error) {
      this.sendResponse({
        jsonrpc: '2.0',
        id: request.id,
        error: {
          code: -32603,
          message: error.message
        }
      });
    }
  }

  start() {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      terminal: false
    });

    rl.on('line', async (line) => {
      try {
        const request = JSON.parse(line);
        await this.handleRequest(request);
      } catch (e) {
        console.error('Parse error:', e);
      }
    });
  }
}

// Start server
const server = new ComputerUseMCPServer();
server.start();
