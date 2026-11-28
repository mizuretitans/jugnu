import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { del, get, patch, post } from './client';
import type {
  Booking, Config, Conversation, Dashboard, Intake, Mentor, MentorshipRequest, Message,
  NewBooking, OwnMentor, Post, StudentBrief, Turn, ChatMessage, CareerPath,
  CareerExplorerInput, CareerExplorerReply,
} from './types';

const CHAT_POLL_MS = 3_000;
const PAGE_POLL_MS = 10_000;
const INTAKE_BUSY_POLL_MS = 2_000;

export const useConfig = () =>
  useQuery({ queryKey: ['config'], queryFn: () => get<Config>('/config'), staleTime: Infinity });

export const useMentors = () =>
  useQuery({ queryKey: ['mentors'], queryFn: () => get<Mentor[]>('/mentors') });

export const useMentor = (id: string) =>
  useQuery({ queryKey: ['mentors', id], queryFn: () => get<Mentor>(`/mentors/${id}`) });

export const useCareerPaths = () =>
  useQuery({
    queryKey: ['career-paths'],
    queryFn: () => get<CareerPath[]>('/career-explorer/paths'),
    staleTime: Infinity,
  });

export const useDashboard = (enabled = true) =>
  useQuery({
    queryKey: ['dashboard'],
    queryFn: () => get<Dashboard>('/dashboard'),
    refetchInterval: PAGE_POLL_MS,
    enabled,
  });

export const useConversation = (id: string) =>
  useQuery({
    queryKey: ['conversation', id],
    queryFn: () => get<Conversation>(`/requests/${id}/messages`),
    refetchInterval: (query) => (query.state.error ? false : CHAT_POLL_MS),
  });

export const useStudentBrief = (id: string, enabled: boolean) =>
  useQuery({
    queryKey: ['brief', id],
    queryFn: () => get<StudentBrief>(`/requests/${id}/student-brief`),
    enabled,
  });

export const usePosts = (field: string) =>
  useQuery({
    queryKey: ['posts', field],
    queryFn: () => get<Post[]>(`/community/${field}/posts`),
    refetchInterval: PAGE_POLL_MS,
  });

export const useIntake = () =>
  useQuery({
    queryKey: ['intake'],
    queryFn: () => get<Intake>('/intake'),
    refetchInterval: (query) => (query.state.data?.busy ? INTAKE_BUSY_POLL_MS : false),
  });

export const useHelper = (enabled: boolean) =>
  useQuery({
    queryKey: ['helper'],
    queryFn: () => get<{ messages: ChatMessage[] }>('/helper/messages'),
    enabled,
  });

/** A mutation that refreshes the given queries whether it succeeds or fails. */
function useAction<TIn, TOut>(run: (input: TIn) => Promise<TOut>, ...refresh: string[][]) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: run,
    onSettled: () =>
      Promise.all(refresh.map((queryKey) => client.invalidateQueries({ queryKey }))),
  });
}

export const useRequestMentor = () =>
  useAction((id: string) => post<MentorshipRequest>(`/mentors/${id}/requests`), ['dashboard']);

export const useAccept = () =>
  useAction((id: string) => post<MentorshipRequest>(`/requests/${id}/accept`), ['dashboard']);

export const useSendMessage = (id: string) =>
  useAction(
    (body: string) => post<Message>(`/requests/${id}/messages`, { body }),
    ['conversation', id],
  );

export const useCreatePost = (field: string) =>
  useAction((body: string) => post<Post>(`/community/${field}/posts`, { body }), ['posts', field]);

export const useBook = () =>
  useAction((booking: NewBooking) => post<Booking>('/bookings', booking), ['dashboard'], ['mentors']);

export const useConfirmBooking = () =>
  useAction((id: string) => post<Booking>(`/bookings/${id}/confirm`), ['dashboard']);

export const useUpdateRate = () =>
  useAction(
    (rupees: number) => patch<OwnMentor>('/mentor/rate', { hourly_rate_rupees: rupees }),
    ['dashboard'], ['mentors'],
  );

export const useStartIntake = () =>
  useAction((_: void) => post<Intake>('/intake/start'), ['intake']);

export const useSendIntake = () =>
  useAction((text: string) => post<Turn>('/intake/messages', { text }), ['intake'], ['dashboard']);

export const useRestartIntake = () =>
  useAction((_: void) => del('/intake'), ['intake'], ['dashboard'], ['helper']);

export const useAskHelper = () =>
  useAction(
    (text: string) => post<{ messages: ChatMessage[] }>('/helper/messages', { text }),
    ['helper'],
  );

export const useAskCareerExplorer = () =>
  useMutation({
    mutationFn: (input: CareerExplorerInput) =>
      post<CareerExplorerReply>('/career-explorer/messages', input),
  });
