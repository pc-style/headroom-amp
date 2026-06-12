/** Minimal Amp plugin types for local typechecking only. */

export interface PluginAPI {
  logger: { log(message: string): void };
  configuration: { get(): Promise<Record<string, unknown>> };
  createStatusItem(initial: { text: string }): {
    update(value: { text: string }): void;
  };
  on<T extends string>(
    event: T,
    handler: (event: any, ctx: any) => Promise<any> | any,
  ): unknown;
  registerTool(definition: Record<string, unknown>): unknown;
}
