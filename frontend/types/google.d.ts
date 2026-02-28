// Type declarations for Google Identity Services (GSI)
interface Window {
    google?: {
        accounts?: {
            id?: {
                initialize: (config: {
                    client_id: string;
                    callback: (response: { credential: string }) => void;
                    auto_select?: boolean;
                    cancel_on_tap_outside?: boolean;
                }) => void;
                renderButton: (
                    element: HTMLElement | null,
                    options: {
                        theme?: 'outline' | 'filled_blue' | 'filled_black';
                        size?: 'large' | 'medium' | 'small';
                        width?: number;
                        text?: 'signin_with' | 'signup_with' | 'continue_with';
                        locale?: string;
                    }
                ) => void;
                prompt: () => void;
                cancel: () => void;
            };
        };
    };
}
