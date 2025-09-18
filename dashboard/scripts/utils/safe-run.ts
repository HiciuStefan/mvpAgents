import { spawn, ChildProcess } from 'node:child_process';
import { join } from 'path';
import { platform } from 'os';

/**
 * Cross-platform safe spawn for local tools like tsx, pnpm, etc.
 */
export async function safeRun(
  command: string,
  args: string[] = [],
  silent = false
): Promise<number> {
  return new Promise((resolve, reject) => {
    const isWindows = platform() === 'win32';

    const proc = spawn(command, args, {
      stdio: silent ? ['ignore', 'inherit', 'inherit'] : 'inherit',
      shell: true, // Always use shell for robustness
    });

    proc.on('error', err => {
      console.error(`Failed to spawn ${command}:`, err);
      reject(err);
    });

    proc.on('exit', code => {
      if (code === null) {
        reject(new Error(`${command} exited with null code`));
      } else {
        resolve(code);
      }
    });
  });
}

/**
 * Cross-platform safe spawn that returns the child process for long-running commands
 */
export function safeSpawn(
  command: string,
  args: string[] = [],
  options: { stdio?: 'inherit' | 'pipe' } = {}
): ChildProcess {
  return spawn(command, args, {
    stdio: options.stdio || 'inherit',
    shell: true, // Always use shell for robustness
  });
}
