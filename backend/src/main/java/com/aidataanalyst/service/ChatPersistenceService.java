package com.aidataanalyst.service;

import com.aidataanalyst.entity.ChatMessage;
import com.aidataanalyst.entity.ChatSession;
import com.aidataanalyst.entity.User;
import com.aidataanalyst.repository.ChatMessageRepository;
import com.aidataanalyst.repository.ChatSessionRepository;
import com.aidataanalyst.repository.UserRepository;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

@Service
public class ChatPersistenceService {

    private final ChatSessionRepository chatSessionRepository;
    private final ChatMessageRepository chatMessageRepository;
    private final UserRepository userRepository;

    public ChatPersistenceService(ChatSessionRepository chatSessionRepository,
                                  ChatMessageRepository chatMessageRepository, UserRepository userRepository) {
        this.chatSessionRepository = chatSessionRepository;
        this.chatMessageRepository = chatMessageRepository;
        this.userRepository = userRepository;
    }

    @Transactional
    public void recordExchange(Long datasetId, String question, String answer, String email) {
        User user = userRepository.findByEmailIgnoreCase(email)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "User is unavailable"));
        ChatSession session = chatSessionRepository
                .findFirstByDatasetIdAndUserIdOrderByIdAsc(datasetId, user.getId())
                .orElseGet(() -> chatSessionRepository.save(new ChatSession(datasetId, user.getId())));
        chatMessageRepository.save(new ChatMessage(session.getId(), "user", question));
        chatMessageRepository.save(new ChatMessage(session.getId(), "assistant", answer));
    }
}